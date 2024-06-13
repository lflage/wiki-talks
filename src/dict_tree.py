import re
from treelib import Node, Tree
import pickle
import pprint


date_signature = "\d{1,2}:\d{2}, \d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4} \(UTC\)"

def check_depth(text, base=1):
    # considers that every string has to start with a :
    match = re.match(":+",text)
    if match:
        start,end = match.span()
        depth = end - start
        return depth + base
    else:
        return base

class Reply(object):
        def __init__(self, text): 
            self.content = text

test_2 = """Is Australia not an island, a continent, ''and'' a country? ~ [[User:RTG|<font color="Brown" size="2" face="Impact">R</font>]].[[User_Talk:RTG|<font color="brown" size="2" face="impact">T</font>]].[[Special:Contributions/RTG|<font color="brown" size="2" face="impact">G</font>]] 04:27, 28 October 2008 (UTC)
:Yes it's an island, and yes it's a country. (Some consider it part of the content of Oceania, but the other two things are not debated.) I don't see what your point is, though. [[User:Giggy|Giggy]] ([[User talk:Giggy|talk]]) 04:33, 28 October 2008 (UTC)

:I also can't see your point.  We mention both points but discuss the country before the continent because that is what we think most people are interested in.  If you think we should mention the continent first, please explain your reasoning.--[[User:Matilda|Matilda]] ([[User talk:Matilda|talk]]) 05:51, 28 October 2008 (UTC)
I had a read of it and the first line said "Australia is a country" but as far as I know Australia is an island, a continent, and a country, and unique in that, so it looked a bit incomplete. Largest one country island in the world and all that and fairly peaceful too it seems. ~ [[User:RTG|<font color="Brown" size="2" face="Impact">R</font>]].[[User_Talk:RTG|<font color="brown" size="2" face="impact">T</font>]].[[Special:Contributions/RTG|<font color="brown" size="2" face="impact">G</font>]] 13:20, 29 October 2008 (UTC)
::I have had a bit of a go at rewording - what do you think?--[[User:Matilda|Matilda]] ([[User talk:Matilda|talk]]) 20:09, 29 October 2008 (UTC)
::For me it's very long ,and not very complex and could be a GA. ~ [[User:RTG|<font color="Brown" size="2" face="Impact">R</font>]].[[User_Talk:RTG|<font color="brown" size="2" face="impact">T</font>]].[[Special:Contributions/RTG|<font color="brown" size="2" face="impact">G</font>]] 20:36, 29 October 2008 (UTC)

:::needs references and there are some mistakes - for example cattle ranching in the centre - but I will work on it (slowly)--[[User:Matilda|Matilda]] ([[User talk:Matilda|talk]]) 20:46, 29 October 2008 (UTC)

::::I should point out that the Australian Continent has two (2) countries on it, Hutt River achieved legal indipendence in 1972. [[User:Nford24|Nford24]] ([[User talk:Nford24|talk]]) 04:39, 23 June 2012 (UTC)
::I don't think references are a real thing  20:36, 29 October 2008 (UTC)
::same level comment 20:36, 29 October 2008 (UTC)
::yet another same level comment 20:36, 29 October 2008 (UTC)
"""
test_2 = re.sub("\n+", "\n", test_2)
test_2 = test_2.strip()

search = re.search(date_signature, test_2)

thread_text = re.search(date_signature, test_2).string[:search.end()]
replies_text = re.search(date_signature, test_2).string[search.end():]

thread = {"message":thread_text,
            "replies": []}
            
stack = [thread]
depth = 0
for ix, split in enumerate(replies_text.split("\n:")[1:],start=1):

    # enumerate starts at 1
    
    split = split.strip()
    depth = check_depth(split)

    text = re.search(date_signature, split).string[:search.end()][depth-1:]
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
    #depth check
    depth

pprint.pprint(thread)
# tree.save2file("parse_tree.txt",data_property='content')
# with open("parse_tree.pkl", "wb") as f:
#     pickle.dump(tree, f)
# with open("parse_tree.pkl", "rb") as f:
#     tree_load = pickle.load(f)
# tree_load.save2file("parse_tree.txt",data_property='content')
# 