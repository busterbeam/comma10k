#!/usr/bin/env python3
from os.path import isfile
from subprocess import check_output

def tx(path):
  if "/sa" in path:
    begining, end = path.split("/sa")
    numeral, name = int(end[:5]), end[5:]
    return f"{begining}/{numeral+5000:05}{name}")
  return path

def git_commits():
  # https://stackoverflow.com/questions/5669621/git-find-out-which-files-have-had-the-most-commits
  filenames = set()
  command = "git rev-list --objects --all | awk '$2' | sort -k2 | uniq -cf1 | sort -rn"
  al_set = set()
  for commit in check_output(command, shell=True).split('\n'):
    commit_split = commit.split()
    if len(commit_split) == 3:
      count, _, filename = commit_split
      count, filename = int(count), tx(filename)
      if isfile(filename) and filename.startswith("masks/"):
        if count > 1:
          filenames.add(filename)
        al_set.add(filename)
  return al_set, filenames

def optional_output(al_set, filenames):
  missing_count = len(al_set) - len(filenames)
  question = (
    f" Do you want to list {missing_count} mask"
    f"{'s' * (missing_count > 0)} that are missing? [n]/y")
  if input(question) == 'y':
    print(al_set.difference(filenames))

def save(filenames):
  # saving with a little style
  print(" Saving", end='\r')
  with open("files_trainable", "w") as trainables_file:
    total = len(filenames)
    for num, filename in enumerate(filenames):
      trainables_file.write(filename + '\n')
      print("\x1b[2K", " Saving {num/total:.0%}", end='\r')
  print(" Saved", end="\r\x1b[2K")

if __name__ == "__main__":
  al_set, filenames = git_commits()
  
  optional_output(al_set, filenames)
  
  save(filenames)

  print(f" {len(filenames)} out of {len(al_set)} labelled,",
        f" {len(filenames)/len(al_set):.2%} complete")
