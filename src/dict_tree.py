import re
from log_utils import setup_logger

dict_tree_logger = setup_logger("dict_tree_logger", "../logs/dict_tree_logger.log")

date_signature = "\d{1,2}:\d{2}, \d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \(UTC\)"

def check_depth(text, base=1):
    # considers that every string has to start with a :
    match = re.match(":+",text)
    if match:
        start,end = match.span()
        depth = end - start
        return depth + base
    else:
        return base

def thread_tree(text):
    
    text = re.sub("\n+", "\n", text)
    text = text.strip()

    search = re.search(date_signature, text)
    try:
        thread_text = re.search(date_signature, text).string[:search.end()]
        replies_text = re.search(date_signature, text).string[search.end():]
    except AttributeError:
        return None

    thread = {"message":thread_text,
                "replies": []}
    if not replies_text.strip():
        return thread
    stack = [thread]
    for ix, split in enumerate(replies_text.split("\n:")[1:],start=1):

        # enumerate starts at 1
        
        split = split.strip()
        depth = check_depth(split)
        try:
            search_result = re.search(date_signature, split)
            text = search_result.string[:search_result.end()][depth-1:]

        except AttributeError as e:
            # TODO: add a log statement to capture which file generated the error
            # Returns empty dict if can't parse a correct structure
            dict_tree_logger.debug(e)
            return {}

        reply = {"text": text,
                "replies":[]}

        if depth  > len(stack):
            stack[-1]["replies"].append(reply)

        elif depth == len(stack):
            stack[-1]["replies"].append(reply)

        elif depth < len(stack):
            dif = len(stack) - depth
            stack = stack[:-dif]
            stack[-1]["replies"].append(reply)

        stack.append(reply)
    return thread

if __name__=="__main__":
    print("main")