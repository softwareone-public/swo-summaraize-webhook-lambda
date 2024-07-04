del /q dist function.zip

esbuild src/index.ts ^
  --bundle ^
  --minify ^
  --sourcemap ^
  --platform=node ^
  --target=es2022 ^
  --outfile=dist/index.js && ^
cd dist && ^
copy *.* .. /Y && ^
cd .. && ^
7z a -tzip function.zip index.js* && ^
del /q index.js index.js.map && ^
aws lambda update-function-code ^
  --function-name summaraize-webhook-prod ^
  --zip-file fileb://function.zip ^
  --no-cli-pager
