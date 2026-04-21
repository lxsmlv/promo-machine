import { useState } from 'react'

const TABS = [
  { id: 'projects', label: '📁 Проекты' },
  { id: 'trends', label: '🔍 Тренды' },
  { id: 'analysis', label: '📊 Анализ' },
  { id: 'generate', label: '✨ Генерация' },
  { id: 'export', label: '📦 Экспорт' },
]

export default function App() {
  const [tab, setTab] = useState('projects')

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0f', color: '#fff', display: 'flex' }}>
      <nav style={{
        width: 220, borderRight: '1px solid rgba(255,255,255,0.1)',
        padding: 16, display: 'flex', flexDirection: 'column', gap: 4,
      }}>
        <h1 style={{
          fontSize: 18, fontWeight: 800, marginBottom: 24, paddingLeft: 12,
          textShadow: '0 0 20px rgba(139,92,246,0.5)',
        }}>
          🎬 Promo Machine
        </h1>
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              background: tab === t.id ? 'rgba(139,92,246,0.15)' : 'transparent',
              border: tab === t.id ? '1px solid rgba(139,92,246,0.3)' : '1px solid transparent',
              color: tab === t.id ? '#c4b5fd' : '#a1a1aa',
              borderRadius: 8, padding: '10px 12px', textAlign: 'left',
              cursor: 'pointer', fontSize: 14, fontWeight: 500,
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main style={{ flex: 1, padding: 24, overflowY: 'auto' }}>
        {tab === 'projects' && <ProjectsTab />}
        {tab === 'trends' && <TrendsTab />}
        {tab === 'analysis' && <AnalysisTab />}
        {tab === 'generate' && <GenerateTab />}
        {tab === 'export' && <ExportTab />}
      </main>
    </div>
  )
}

function ProjectsTab() {
  const [projects, setProjects] = useState<any[]>([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(false)

  const load = async () => {
    const res = await fetch('/api/projects')
    setProjects(await res.json())
  }

  useState(() => { load() })

  const create = async () => {
    if (!name) return
    setLoading(true)
    const form = new FormData()
    form.append('name', name)
    form.append('description', desc)
    await fetch('/api/projects', { method: 'POST', body: form })
    setName(''); setDesc('')
    await load()
    setLoading(false)
  }

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Проекты</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          placeholder="Название приложения"
          value={name} onChange={e => setName(e.target.value)}
          style={{ flex: 1, background: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', color: '#fff', fontSize: 14 }}
        />
        <input
          placeholder="Описание"
          value={desc} onChange={e => setDesc(e.target.value)}
          style={{ flex: 2, background: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', color: '#fff', fontSize: 14 }}
        />
        <button onClick={create} disabled={loading}
          style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, padding: '8px 20px', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: 14 }}
        >
          {loading ? '...' : '+ Создать'}
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {projects.map((p: any) => (
          <div key={p.id} style={{
            background: '#111118', border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12, padding: 16,
          }}>
            <div style={{ fontWeight: 600 }}>{p.name}</div>
            <div style={{ fontSize: 12, color: '#71717a', marginTop: 4 }}>{p.description}</div>
            <div style={{ fontSize: 11, color: '#52525b', marginTop: 4 }}>ID: {p.id}</div>
          </div>
        ))}
        {projects.length === 0 && <div style={{ color: '#52525b', fontSize: 14 }}>Нет проектов. Создайте первый.</div>}
      </div>
    </div>
  )
}

function TrendsTab() {
  const [trends, setTrends] = useState<any[]>([])
  const [urls, setUrls] = useState('')
  const [scanning, setScanning] = useState(false)

  const load = async () => {
    const res = await fetch('/api/trends')
    setTrends(await res.json())
  }

  useState(() => { load() })

  const scan = async () => {
    if (!urls) return
    setScanning(true)
    await fetch(`/api/scan?urls=${encodeURIComponent(urls)}&platform=tiktok`, { method: 'POST' })
    // Poll status
    const poll = setInterval(async () => {
      const res = await fetch('/api/scan/status')
      const status = await res.json()
      if (!status.running) {
        clearInterval(poll)
        setScanning(false)
        await load()
      }
    }, 2000)
  }

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Тренды</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          placeholder="Вставьте URL видео через запятую"
          value={urls} onChange={e => setUrls(e.target.value)}
          style={{ flex: 1, background: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', color: '#fff', fontSize: 14 }}
        />
        <button onClick={scan} disabled={scanning}
          style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, padding: '8px 20px', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: 14 }}
        >
          {scanning ? '⏳ Сканирую...' : '🔍 Сканировать'}
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {trends.map((t: any) => (
          <div key={t.id} style={{
            background: '#111118', border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12, padding: 16, display: 'flex', justifyContent: 'space-between',
          }}>
            <div>
              <div style={{ fontSize: 13 }}>{t.description?.slice(0, 80) || t.url}</div>
              <div style={{ fontSize: 11, color: '#71717a', marginTop: 4 }}>
                👁 {t.views?.toLocaleString()} · ❤️ {t.likes?.toLocaleString()} · 💬 {t.comments?.toLocaleString()} · ⏱ {t.duration}s
              </div>
            </div>
            {t.file_path && <span style={{ color: '#22c55e', fontSize: 12 }}>✓ Скачано</span>}
          </div>
        ))}
        {trends.length === 0 && <div style={{ color: '#52525b', fontSize: 14 }}>Нет трендов. Вставьте URL и сканируйте.</div>}
      </div>
    </div>
  )
}

function AnalysisTab() {
  const [patterns, setPatterns] = useState<any>(null)
  const [analyzing, setAnalyzing] = useState(false)

  const analyze = async () => {
    setAnalyzing(true)
    await fetch('/api/analyze', { method: 'POST' })
    const poll = setInterval(async () => {
      const res = await fetch('/api/analyze/status')
      const status = await res.json()
      if (!status.running) {
        clearInterval(poll)
        setAnalyzing(false)
        const p = await fetch('/api/patterns')
        setPatterns(await p.json())
      }
    }, 3000)
  }

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Анализ трендов</h2>
      <button onClick={analyze} disabled={analyzing}
        style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)', border: 'none', borderRadius: 8, padding: '10px 24px', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: 14, marginBottom: 16 }}
      >
        {analyzing ? '⏳ Анализирую...' : '🧠 Анализировать тренды'}
      </button>
      {patterns && (
        <pre style={{ background: '#111118', borderRadius: 12, padding: 16, fontSize: 12, overflow: 'auto', color: '#a1a1aa' }}>
          {JSON.stringify(patterns, null, 2)}
        </pre>
      )}
    </div>
  )
}

function GenerateTab() {
  const [projectId, setProjectId] = useState('')
  const [scripts, setScripts] = useState<any>(null)
  const [hooks, setHooks] = useState<any>(null)
  const [copy, setCopy] = useState<any>(null)
  const [loading, setLoading] = useState('')

  const genScripts = async () => {
    if (!projectId) return
    setLoading('scripts')
    const res = await fetch(`/api/generate/scripts?project_id=${projectId}&count=5&duration=30`, { method: 'POST' })
    setScripts(await res.json())
    setLoading('')
  }

  const genHooks = async () => {
    if (!projectId) return
    setLoading('hooks')
    const res = await fetch(`/api/generate/hooks?project_id=${projectId}`, { method: 'POST' })
    setHooks(await res.json())
    setLoading('')
  }

  const genCopy = async () => {
    if (!projectId) return
    setLoading('copy')
    const res = await fetch(`/api/generate/copy?project_id=${projectId}`, { method: 'POST' })
    setCopy(await res.json())
    setLoading('')
  }

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Генерация контента</h2>
      <input
        placeholder="Project ID"
        value={projectId} onChange={e => setProjectId(e.target.value)}
        style={{ background: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: '8px 12px', color: '#fff', fontSize: 14, marginBottom: 16, width: 200 }}
      />
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button onClick={genScripts} disabled={!!loading}
          style={{ background: '#7c3aed', border: 'none', borderRadius: 8, padding: '8px 16px', color: '#fff', cursor: 'pointer', fontSize: 13 }}>
          {loading === 'scripts' ? '...' : '📝 Сценарии'}
        </button>
        <button onClick={genHooks} disabled={!!loading}
          style={{ background: '#7c3aed', border: 'none', borderRadius: 8, padding: '8px 16px', color: '#fff', cursor: 'pointer', fontSize: 13 }}>
          {loading === 'hooks' ? '...' : '🎣 Хуки'}
        </button>
        <button onClick={genCopy} disabled={!!loading}
          style={{ background: '#7c3aed', border: 'none', borderRadius: 8, padding: '8px 16px', color: '#fff', cursor: 'pointer', fontSize: 13 }}>
          {loading === 'copy' ? '...' : '📋 Тексты'}
        </button>
      </div>
      {scripts && <Section title="Сценарии" data={scripts} />}
      {hooks && <Section title="Хуки" data={hooks} />}
      {copy && <Section title="Тексты" data={copy} />}
    </div>
  )
}

function ExportTab() {
  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Экспорт</h2>
      <div style={{ color: '#52525b', fontSize: 14 }}>Сначала сгенерируйте видео во вкладке Генерация.</div>
    </div>
  )
}

function Section({ title, data }: { title: string; data: any }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8, color: '#a78bfa' }}>{title}</h3>
      <pre style={{ background: '#111118', borderRadius: 12, padding: 16, fontSize: 11, overflow: 'auto', color: '#a1a1aa', maxHeight: 400 }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}
