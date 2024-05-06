rm -rf ./package
rm rag_index_zipped.zip
pip install --target ./package -r ./requirements.txt

cd package
zip -r ../rag_index_zipped.zip .
cd ..
zip rag_index_zipped.zip ragindex.py