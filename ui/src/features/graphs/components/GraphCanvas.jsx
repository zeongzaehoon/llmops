import AgentNode from './AgentNode'
import Button from '@/components/inputs/Button'
import styles from './GraphCanvas.module.scss'

function ArrowConnector({ label }) {
  return (
    <div className={styles.arrow}>
      <span className={styles.arrowLine} />
      <span className={styles.arrowHead} />
      {label && <span className={styles.arrowLabel}>{label}</span>}
    </div>
  )
}

function LinearLayout({ agents, onChangeAgent, onRemoveAgent, onAddAgent }) {
  return (
    <div className={styles.linearFlow}>
      {agents.map((agent, i) => (
        <div key={i} className={styles.linearItem}>
          <AgentNode
            agent={agent}
            index={i}
            onChange={onChangeAgent}
            onRemove={onRemoveAgent}
            removable={agents.length > 1}
          />
          {i < agents.length - 1 && <ArrowConnector />}
        </div>
      ))}
      <div className={styles.addBtnWrapper}>
        <Button variant="ghost" size="sm" onClick={onAddAgent}>
          + Add Agent Node
        </Button>
      </div>
    </div>
  )
}

function DebateLayout({ agents, onChangeAgent, onRemoveAgent, onAddAgent, moderator }) {
  const debaters = agents.filter((_, i) => i < agents.length)

  return (
    <div className={styles.debateFlow}>
      <div className={styles.debateAgents}>
        {debaters.map((agent, i) => (
          <div key={i} className={styles.debateItem}>
            <AgentNode
              agent={agent}
              index={i}
              onChange={onChangeAgent}
              onRemove={onRemoveAgent}
              removable={debaters.length > 2}
            />
            {i < debaters.length - 1 && (
              <div className={styles.debateArrows}>
                <span className={styles.debateArrowRight}>{'\u2192'}</span>
                <span className={styles.debateArrowLeft}>{'\u2190'}</span>
              </div>
            )}
          </div>
        ))}
        <div className={styles.addBtnWrapper}>
          <Button variant="ghost" size="sm" onClick={onAddAgent}>
            + Add Agent
          </Button>
        </div>
      </div>

      <div className={styles.debateBottom}>
        <div className={styles.debateConnector}>
          <span className={styles.verticalLine} />
          <span className={styles.arrowHead} />
        </div>
        <div className={styles.moderatorNode}>
          <span className={styles.moderatorLabel}>Moderator</span>
          <span className={styles.moderatorName}>{moderator || 'Not set'}</span>
        </div>
      </div>
    </div>
  )
}

function ParallelLayout({ agents, onChangeAgent, onRemoveAgent, onAddAgent }) {
  return (
    <div className={styles.parallelFlow}>
      <div className={styles.parallelFanOut}>
        <div className={styles.parallelBranches}>
          {agents.map((agent, i) => (
            <div key={i} className={styles.parallelBranch}>
              <div className={styles.branchLine} />
              <AgentNode
                agent={agent}
                index={i}
                onChange={onChangeAgent}
                onRemove={onRemoveAgent}
                removable={agents.length > 2}
              />
              <div className={styles.branchLine} />
            </div>
          ))}
        </div>
        <div className={styles.addBtnWrapperCentered}>
          <Button variant="ghost" size="sm" onClick={onAddAgent}>
            + Add Agent
          </Button>
        </div>
      </div>

      <div className={styles.aggregatorNode}>
        <span className={styles.aggregatorIcon}>{'\u2192'}</span>
        <span className={styles.aggregatorLabel}>Aggregator</span>
      </div>
    </div>
  )
}

function RouterLayout({ agents, onChangeAgent, onRemoveAgent, onAddAgent }) {
  return (
    <div className={styles.routerFlow}>
      <div className={styles.routerNode}>
        <span className={styles.routerIcon}>R</span>
        <span className={styles.routerLabel}>Router</span>
      </div>

      <div className={styles.routerBranches}>
        {agents.map((agent, i) => (
          <div key={i} className={styles.routerBranch}>
            <div className={styles.routerArrow}>
              <span className={styles.routerCondition}>?</span>
              <span className={styles.arrowLine} />
              <span className={styles.arrowHead} />
            </div>
            <AgentNode
              agent={agent}
              index={i}
              onChange={onChangeAgent}
              onRemove={onRemoveAgent}
              removable={agents.length > 2}
            />
          </div>
        ))}
      </div>

      <div className={styles.addBtnWrapperCentered}>
        <Button variant="ghost" size="sm" onClick={onAddAgent}>
          + Add Branch
        </Button>
      </div>
    </div>
  )
}

export default function GraphCanvas({
  type,
  agents,
  onChangeAgent,
  onRemoveAgent,
  onAddAgent,
  moderator,
}) {
  const layoutProps = { agents, onChangeAgent, onRemoveAgent, onAddAgent }

  return (
    <div className={styles.canvas}>
      <div className={styles.canvasInner}>
        {type === 'linear' && <LinearLayout {...layoutProps} />}
        {type === 'debate' && <DebateLayout {...layoutProps} moderator={moderator} />}
        {type === 'parallel' && <ParallelLayout {...layoutProps} />}
        {type === 'router' && <RouterLayout {...layoutProps} />}
      </div>
    </div>
  )
}
