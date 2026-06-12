import RecommendationCard from './RecommendationCard'

export default function ResultsView({ data }) {
  return (
    <div className='results-container'>
      <div className='conditions-summary'>
        <p className='conditions-label'>Inferred Conditions</p>
        <div className='condition-chips'>
          {data.inferred_conditions.map((c, i) => (
            <span key={i} className='condition-chip'>{c}</span>
          ))}
        </div>
      </div>

      <h2 className='rec-section-title'>Recommendations</h2>
      <div className='rec-grid'>
        {data.recommendations.map((rec, i) => (
          <RecommendationCard key={i} {...rec} />
        ))}
      </div>

      <p className='disclaimer'>{data.disclaimer}</p>
    </div>
  )
}
