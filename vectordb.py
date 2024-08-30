from pinecone import Pinecone

index = pc.Index("slay-vector-db")

array =[]

ans = index.query(
    vector=[0.1]*1024,
    top_k=5,
    include_values=True,
    include_metadata=True,
)

for i in range(len(ans['matches'])):
    array.append(ans['matches'][i]['id'])

print(array)
