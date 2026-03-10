import styles from './VendorSelector.module.scss'

const VENDOR_LABELS = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google',
  xai: 'X.AI',
  bedrock: 'Bedrock',
  azure: 'Azure',
}

export default function VendorSelector({
  vendors = [],
  selected,
  onSelect,
  modelCounts = {},
}) {
  return (
    <div className={styles.group}>
      {vendors.map((vendor) => (
        <button
          key={vendor}
          className={`${styles.vendorBtn} ${vendor === selected ? styles.active : ''}`}
          onClick={() => onSelect(vendor)}
        >
          <span className={styles.name}>{VENDOR_LABELS[vendor] || vendor}</span>
          {modelCounts[vendor] != null && (
            <span className={styles.count}>{modelCounts[vendor]}</span>
          )}
        </button>
      ))}
    </div>
  )
}
