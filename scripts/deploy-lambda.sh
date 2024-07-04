#!/bin/bash

rm -rf dist

rm -rf funtion.zip

esbuild src/index.ts --bundle --minify --sourcemap --platform=node --target=es2022 --outfile=dist/index.js

cd dist

cp -r *.* ..

cd ..

zip -r function.zip index.js index.js.map

rm -rf index.js

rm -rf index.js.map

aws lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://function.zip --no-cli-pager
