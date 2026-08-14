#!/bin/bash
# ls-remote sweep of the DeepStack-Leduc fork network: flag forks whose
# refs differ from upstream (da416f96 master / bd344ca initial).
UP1=da416f9646725def43e668851593de13ead8b607
while read u; do
  out=$(timeout 30 git ls-remote "https://github.com/$u/DeepStack-Leduc" 2>/dev/null)
  if [ -z "$out" ]; then echo "GONE $u"; continue; fi
  extra=$(echo "$out" | awk '{print $1}' | sort -u | grep -v "^$UP1$" | wc -l)
  nrefs=$(echo "$out" | wc -l)
  if [ "$extra" -gt 0 ]; then
    echo "DIFF $u refs=$nrefs"
    echo "$out" | sed "s/^/    $u /"
  else
    echo "same $u"
  fi
done
