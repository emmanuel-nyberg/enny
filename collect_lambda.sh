#!/usr/bin/env bash
ENNY_URL=$(zappa status | awk '/Gateway URL/{print $4}')
for i in $(cat NDX); do
    curl $ENNY_URL/api/v1.0/collector/collect/$i
    sleep 13
done