import json, os, argparse
from transformers import pipeline
from tqdm import tqdm
from src.utils.date_signatures import iso_639_dict

from pprint import pprint

LABEL_MAP = {"LABEL_0": "neutral", "LABEL_1": "toxic"}
DRY_RUN = False

if not DRY_RUN:
    classifier = pipeline(
        "text-classification",
        model="textdetox/xlmr-large-toxicity-classifier-v2",
        top_k=None,      # returns both neutral and toxic scores
        device=0
    )

def iter_messages(page: dict):
    """
    Yields (thread_idx, node_path, message) for every message in a page.
    node_path is a tuple of reply indices: () = thread root, (i,) = first-level reply i, etc.
    """
    # print(type(page.get("threads")))
    for thread_idx, thread in enumerate(page.get("threads", [])):
        yield thread_idx, (), thread["message"]
        yield from _iter_replies(thread_idx, (), thread.get("replies", []))

def _iter_replies(thread_idx, path, replies):
    # print(replies)
    for i, reply in enumerate(replies):
        child_path = path + (i,)
        # print(reply)
        yield thread_idx, child_path, reply["text"]
        yield from _iter_replies(thread_idx, child_path, reply.get("replies", []))

def scores_from_result_detoxify(result):
    """Collapse classifier output into a plain {label: score} dict."""
    return {item["label"]: item["score"] for item in result}


def scores_from_result_toxicity_classifier(result):
    return {LABEL_MAP.get(item["label"], item["label"]): item["score"] for item in result}

def classify_page(page: dict, classifier, batch_size: int = 32) -> list[dict]:
    """
    Returns a list of sidecar records for all messages in the page.
    Uses batched inference for efficiency.
    """
    # Collect everything first so we can batch
    records_meta = []  # (thread_idx, node_path)
    texts = []

    for thread_idx, node_path, message in iter_messages(page):
        records_meta.append((thread_idx, node_path))
        texts.append(message)


    if not texts:
        return []

    # Batch classify
    results = classifier(texts, batch_size=batch_size, truncation=True, max_length=512)

    sidecar_records = []
    for (thread_idx, node_path), result in zip(records_meta, results):
        sidecar_records.append({
            "page_id": page["id"],
            "thread_idx": thread_idx,
            "node_path": list(node_path),  # JSON can't store tuples
            "scores": scores_from_result_toxicity_classifier(result)
        })

    return sidecar_records


# --- Main loop ---
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
        """Generates wiki-talks dataset statistics
        """)

    parser.add_argument('-i','--input', type=str,
        help='path to input')
    parser.add_argument('-l', '--langs', type=str, nargs='*', default=[],
                     help='ISO 639 language codes, e.g. -l pt fr')
    args = parser.parse_args()

    input_path = args.input
    langs = args.langs if args.langs else iso_639_dict.keys()

    for lg in langs:
        if lg not in iso_639_dict.keys():
            raise ValueError(f"{lg} not in valid languages")

    for base, dirs, jsonl_list in tqdm(os.walk(args.input)):
        for jsonl_file in jsonl_list:
            if "sidecar" in jsonl_file or "checkpoint" in jsonl_file:
                continue
            if not jsonl_file.endswith("jsonl"):
                continue
            cur_lg = base.split("/")[-1]
            if cur_lg not in langs:
                continue
            
            full_path = os.path.join(base,jsonl_file)
            sidecar_path = f"{full_path.split('.jsonl')[0]}.sidecar.jsonl"
            first = True

            if DRY_RUN:
                print(full_path)
                print(sidecar_path)
                x = input()
                continue

            with open(full_path) as f_in, open(sidecar_path, "w") as f_out:
                for line in tqdm(f_in):
                    page = json.loads(line)
                    records = classify_page(page, classifier, batch_size=64)
                    for record in records:
                        f_out.write(json.dumps(record, ensure_ascii=False) + "\n") 
                    if first:
                        first = False
                        print(records)
