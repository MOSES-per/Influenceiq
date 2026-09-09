#!/bin/bash

countjava(){
  count=$(find . -name "*.java" | wc -l)
  echo "Java Files: $count"
}

countjava
