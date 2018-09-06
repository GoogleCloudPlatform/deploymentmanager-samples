#!/bin/zsh -x

WHITELIST=""

REQUESTED=$(ls | grep 'example' | sed 's/\.yaml//g')
EXISTING=$(gcloud deployment-manager deployments list | awk '{print $1}' | sed 1,1d)

TO_CREATE=$(diff --new-line-format="" --unchanged-line-format="" <(echo $REQUESTED) <(echo $EXISTING))
TO_UPDATE=$(sort <(echo $EXISTING) <(echo $REQUESTED) | uniq -d)
TO_DELETE=$(diff --new-line-format="" --unchanged-line-format="" <(echo $EXISTING) <(echo $REQUESTED))

# exclude projects in whitelist
TO_CREATE=$(comm -23 <(echo $TO_CREATE) <(echo $WHITELIST))
TO_UPDATE=$(comm -23 <(echo $TO_UPDATE) <(echo $WHITELIST))
TO_DELETE=$(comm -23 <(echo $TO_DELETE) <(echo $WHITELIST))

echo $TO_CREATE
echo $TO_UPDATE
echo $TO_DELETE

for i in $(echo $TO_CREATE | sed "s/\\\n/\n/g"); do
  gcloud deployment-manager deployments create ${i} --config ${i}.yaml
done

for i in $(echo $TO_UPDATE | sed "s/\\\n/\n/g"); do
  gcloud deployment-manager deployments update ${i} --config ${i}.yaml
done

for i in $(echo $TO_DELETE | sed "s/\\\n/\n/g"); do
  gcloud deployment-manager deployments delete ${i} --quiet
done
