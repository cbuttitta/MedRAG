from api.services.retriever import retrieve

queries = [
    'foods to avoid with high blood sugar',
    'exercise recommendations for diabetes',
    'dietary changes for high cholesterol',
]

for query in queries:
    print(f'\nQuery: {query}')
    results = retrieve(query, top_k=3)
    for r in results:
        print(f'  [{r["similarity"]:.3f}] {r["source"]} — {r["content"][:80]}...')

