export default function RecommendationCard({ category, action, rationale, sources }) {
  const slug = (category || 'lifestyle').toLowerCase()

  return (
    <div className={`rec-card rec-card--${slug}`}>
      <span className='rec-category'>{category}</span>
      <p className='rec-action'>{action}</p>
      <p className='rec-rationale'>{rationale}</p>
      {sources?.length > 0 && (
        <div className='rec-sources'>
          <span className='sources-label'>
            <svg className='sources-icon' viewBox='0 0 16 16' fill='currentColor'>
              <path d='M2 2.5A2.5 2.5 0 014.5 0h7A2.5 2.5 0 0114 2.5v10.042a.75.75 0 01-1.218.585L8 9.75l-4.782 3.377A.75.75 0 012 12.542V2.5z'/>
            </svg>
            Sources
          </span>
          {sources.map((s, i) => (
            <span key={i} className='source-chip'>{s}</span>
          ))}
        </div>
      )}
    </div>
  )
}
