for dir in *; do
  if [ -d "$dir" ]; then
    for file in "$dir/"*.dot; do
      if [ -f "$file" ]; then
        output="${file%.dot}.png"
        dot "$file" -Tpng -o "$output"
      fi
    done
  fi
done
