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


def thread_no_title(text):
    comment_indent = r"\n:"
    text = re.sub("\n+", "\n", text)
    text = text.strip()

#    print(text)
#    input()
    thread = {'message': "", 'replies': []}

    first_comment = re.search(r"\n:",text)
    if not first_comment:
        thread["message"] = text
        return thread
    
    thread_text = text[:first_comment.start()]
    thread_comments = text[first_comment.end():]

 #   print(thread_text)
#    x = input("thread first message")
    
    thread["message"] = thread_text
    stack = [thread]

#    comment_indent_split = re.split(comment_indent,thread_comments)
    for split in re.split(comment_indent ,thread_comments):
#        print(split)
#        input("split")
        split = split.strip()
        depth = check_depth(split)

        search_result = re.match(r":", split)
        if search_result:
            #if it has indentation 
            text = search_result.string[search_result.start():]
        else:
            text = split
#        print(text)
#        input("text above")
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