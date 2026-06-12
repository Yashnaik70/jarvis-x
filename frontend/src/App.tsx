import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import './App.css'

const endpoint = '/api'
const jsonHeaders = { 'Content-Type': 'application/json' }

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

function prettify(value: unknown) {
  return JSON.stringify(value, null, 2)
}

function createSpeech(audioBase64: string) {
  const audio = new Audio(`data:audio/mpeg;base64,${audioBase64}`)
  audio.play().catch(() => {
    console.warn('Unable to play audio automatically.')
  })
}

function CarVisualizer({ visualizationType }: { visualizationType: string }) {
  const mountRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const mount = mountRef.current
    if (!mount) {
      return
    }

    const width = mount.clientWidth
    const height = mount.clientHeight

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x02091d)

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
    camera.position.set(0, 2.5, 6)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(width, height, false)
    mount.appendChild(renderer.domElement)

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0x99caff, 1)
    directionalLight.position.set(5, 8, 5)
    scene.add(directionalLight)

    const grid = new THREE.GridHelper(20, 20, 0x1d3657, 0x08141f)
    grid.position.y = -0.5
    scene.add(grid)

    const model = new THREE.Group()

    if (visualizationType === 'car') {
      const body = new THREE.Mesh(
        new THREE.BoxGeometry(3.2, 0.8, 1.4),
        new THREE.MeshStandardMaterial({ color: 0x0b6cff, metalness: 0.6, roughness: 0.22 })
      )
      body.position.y = 0.5
      model.add(body)

      const cabin = new THREE.Mesh(
        new THREE.BoxGeometry(1.8, 0.6, 1.05),
        new THREE.MeshStandardMaterial({ color: 0x1465d7, metalness: 0.7, roughness: 0.2 })
      )
      cabin.position.set(0, 0.95, 0)
      model.add(cabin)

      const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x131313, metalness: 0.8, roughness: 0.25 })
      const wheelGeometry = new THREE.CylinderGeometry(0.28, 0.28, 0.45, 24)
      const wheelPositions = [
        [1.15, 0.2, 0.65],
        [-1.15, 0.2, 0.65],
        [1.15, 0.2, -0.65],
        [-1.15, 0.2, -0.65]
      ]
      wheelPositions.forEach(([x, y, z]) => {
        const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial)
        wheel.rotation.z = Math.PI / 2
        wheel.position.set(x, y, z)
        model.add(wheel)
      })
    } else {
      const placeholder = new THREE.Mesh(
        new THREE.SphereGeometry(0.8, 32, 32),
        new THREE.MeshStandardMaterial({ color: 0x223f6f, transparent: true, opacity: 0.35 })
      )
      placeholder.position.y = 0.7
      model.add(placeholder)
    }

    scene.add(model)

    let frameId: number
    const animate = () => {
      model.rotation.y += 0.004
      renderer.render(scene, camera)
      frameId = window.requestAnimationFrame(animate)
    }
    animate()

    const handleResize = () => {
      if (!mount) return
      const newWidth = mount.clientWidth
      const newHeight = mount.clientHeight
      camera.aspect = newWidth / newHeight
      camera.updateProjectionMatrix()
      renderer.setSize(newWidth, newHeight, false)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      window.cancelAnimationFrame(frameId)
      renderer.dispose()
      if (renderer.domElement.parentElement) {
        renderer.domElement.parentElement.removeChild(renderer.domElement)
      }
    }
  }, [visualizationType])

  return (
    <div className="visualizer-panel">
      <div className="viewer-shell" ref={mountRef}>
        <div className="viewer-overlay">
          {visualizationType === 'none' ? 'Say "Show me a 3D car model" or tap the quick command button.' : ''}
        </div>
      </div>
    </div>
  )
}

function App() {
  const [overview, setOverview] = useState('Loading...')
  const [tools, setTools] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am JARVIS-X. Ask me to visualize a 3D car, search the web, or run a tool.'
    }
  ])
  const [inputText, setInputText] = useState('')
  const [visualizationType, setVisualizationType] = useState('none')
  const [visualizationNote, setVisualizationNote] = useState('Ask me to create a 3D car view and I will render it here.')
  const [listening, setListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    fetchOverview()
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (SpeechRecognition) {
      setSpeechSupported(true)
      const recognition = new SpeechRecognition()
      recognition.lang = 'en-US'
      recognition.interimResults = false
      recognition.maxAlternatives = 1
      recognition.onresult = (event: any) => {
        const transcript = event.results?.[0]?.[0]?.transcript?.trim() || ''
        if (transcript) {
          appendMessage({ role: 'user', content: transcript })
          sendCommand(transcript)
        }
      }
      recognition.onend = () => setListening(false)
      recognition.onerror = () => setListening(false)
      recognitionRef.current = recognition
    }
  }, [])

  const appendMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message])
  }

  const fetchOverview = async () => {
    const res = await fetch(`${endpoint}/dashboard/overview`)
    const data = await res.json().catch(() => ({ error: 'Unable to parse response' }))
    setOverview(prettify(data))
  }

  const fetchTools = async () => {
    const res = await fetch(`${endpoint}/tools/list`)
    const data = await res.json().catch(() => ({ error: 'Unable to parse response' }))
    setTools(prettify(data))
  }

  const listenVoice = () => {
    if (!recognitionRef.current) {
      appendMessage({ role: 'assistant', content: 'Voice recognition is not supported in this browser.' })
      return
    }
    setListening(true)
    recognitionRef.current.start()
  }

  const sendCommand = async (command: string) => {
    if (!command.trim()) {
      return
    }
    appendMessage({ role: 'user', content: command })
    appendMessage({ role: 'system', content: 'Thinking...' })
    setInputText('')

    try {
      const res = await fetch(`${endpoint}/assistant/command`, {
        method: 'POST',
        headers: jsonHeaders,
        body: JSON.stringify({ command })
      })
      const data = await res.json().catch(() => ({ message: 'No response from backend' }))

      setMessages((prev) => prev.filter((msg) => msg.role !== 'system' || msg.content !== 'Thinking...'))
      const reply = typeof data.message === 'string' ? data.message : 'I heard you.'
      appendMessage({ role: 'assistant', content: reply })

      if (data.action === 'visualize') {
        setVisualizationType(data.visualization_type || 'car')
        setVisualizationNote(data.visualization_text || 'Rendering your 3D model now.')
      }

      if (data.audio_base64) {
        createSpeech(data.audio_base64)
      }
    } catch (error) {
      setMessages((prev) => prev.filter((msg) => msg.role !== 'system' || msg.content !== 'Thinking...'))
      appendMessage({ role: 'assistant', content: 'Sorry, I could not reach the backend.' })
    }
  }

  const handleSend = () => sendCommand(inputText)

  const sendQuickCommand = (command: string) => {
    setInputText(command)
    sendCommand(command)
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>JARVIS-X</h1>
          <p>Your assistant dashboard with voice, chat, and 3D previews.</p>
        </div>
        <div className="hero-controls">
          <button onClick={fetchOverview}>Refresh status</button>
          <button onClick={fetchTools}>Reload tools</button>
        </div>
      </header>

      <section className="summary-panel">
        <div className="summary-card">
          <h2>System overview</h2>
          <pre>{overview}</pre>
        </div>
        <div className="summary-card">
          <h2>Tools & quick actions</h2>
          <button className="secondary" onClick={fetchTools}>Load tool list</button>
          <pre>{tools}</pre>
        </div>
      </section>

      <main className="main-grid">
        <aside className="side-panel">
          <div className="card">
            <h2>Jarvis chat</h2>
            <div className="chat-window">
              {messages.map((message, index) => (
                <div key={index} className={`chat-bubble ${message.role}`}>
                  <span>{message.content}</span>
                </div>
              ))}
            </div>
            <div className="chat-input-row">
              <input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask JARVIS-X anything..."
                onKeyDown={(event) => event.key === 'Enter' && handleSend()}
              />
              <button onClick={handleSend}>Send</button>
            </div>
            <div className="card-actions">
              <button disabled={!speechSupported || listening} onClick={listenVoice}>
                {listening ? 'Listening…' : 'Talk to Jarvis'}
              </button>
              <button onClick={() => sendQuickCommand('Show me a 3D car model')}>3D car</button>
            </div>
          </div>

          <div className="card">
            <h2>Quick commands</h2>
            <button onClick={() => sendQuickCommand('Search the web for the latest AI assistants')}>
              Search AI assistants
            </button>
            <button onClick={() => sendQuickCommand('List available tools')}>
              List tools
            </button>
            <button onClick={() => sendQuickCommand('Please write a friendly greeting')}>
              Friendly greeting
            </button>
          </div>
        </aside>

        <section className="visualization-card">
          <div className="visualization-header">
            <div>
              <h2>3D visualization</h2>
              <p>{visualizationNote}</p>
            </div>
          </div>
          <CarVisualizer visualizationType={visualizationType} />
        </section>
      </main>
    </div>
  )
}

export default App
