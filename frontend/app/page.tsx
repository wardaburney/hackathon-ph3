'use client';

import { useEffect, useState } from 'react';
import { getTasks, createTask, toggleTaskComplete, deleteTask, getChatResponse } from '../lib/api';
import styles from './pro-style.module.css';

// Task ki interface (achhi practice ke liye)
interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
}

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: string; text: string }[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Token (Testing ke liye hardcoded hai, backend abhi bypass kar raha hai)
  const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdHVzZXIiLCJleHAiOjE3NzEwMTE3NTd9.UAZk66Nvg4gRmZs_xr5Qr3LuyhrXNfeRhoSL4L2Oh10";

  // Initial tasks load karna
  useEffect(() => {
    getTasks(token).then(setTasks);
  }, []);

  // Task toggle logic
  const handleToggle = async (id: number) => {
    const updated = await toggleTaskComplete(id, token);
    if (updated) {
      setTasks((prev) =>
        prev.map((task) => (task.id === updated.id ? updated : task))
      );
    }
  };

  // Task delete logic
  const handleDelete = async (id: number) => {
    const success = await deleteTask(id, token);
    if (success) {
      setTasks((prev) => prev.filter((task) => task.id !== id));
    }
  };

  // AI Chat handle logic (RAG)
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatInput('');
    setChatHistory((prev) => [...prev, { role: 'user', text: userMsg }]);
    setIsChatLoading(true);

    const data = await getChatResponse(userMsg);
    setChatHistory((prev) => [...prev, { role: 'ai', text: data.response }]);
    setIsChatLoading(false);
  };

  return (
    <div className={styles['pro-container']}>
      <h1 className={styles['pro-header']}>AI Task Manager</h1>

      {/* --- Task Form Section --- */}
      <form
        className={styles['pro-form']}
        onSubmit={async (e) => {
          e.preventDefault();
          const target = e.target as any;
          const title = target.title.value;
          const description = target.description.value;

          const newTask = await createTask(title, description, token);
          if (newTask) {
            setTasks((prev) => [...prev, newTask]);
            target.reset();
          }
        }}
      >
        <input name="title" placeholder="Task Title" required />
        <input name="description" placeholder="Description (Optional)" />
        <button type="submit">Add Task</button>
      </form>

      {/* --- Task List Section --- */}
      <ul className={styles['pro-task-list']}>
        {tasks.map((task) => (
          <li
            key={task.id}
            className={`${styles['pro-task']} ${task.completed ? styles.completed : ''}`}
          >
            <span>
              <strong>{task.title}</strong>
              {task.description && ` - ${task.description}`}
            </span>
            <div className={styles['button-group']}>
              <button
                className={styles['complete-btn']}
                onClick={() => handleToggle(task.id)}
              >
                {task.completed ? 'Undo' : 'Complete'}
              </button>
              <button
                className={styles['delete-btn']}
                onClick={() => handleDelete(task.id)}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>

      <hr className={styles['divider']} />

      {/* --- Chatbot (RAG) Section --- */}
      <div className={styles['chat-section']}>
        <h3>Chat with AI (RAG)</h3>
        <div className={styles['chat-window']}>
          {chatHistory.length === 0 && (
            <p style={{ color: '#888', textAlign: 'center' }}>Puchiye AI se apne tasks ke bare mein...</p>
          )}
          {chatHistory.map((msg, i) => (
            <div
              key={i}
              className={msg.role === 'user' ? styles['user-msg'] : styles['ai-msg']}
            >
              <strong>{msg.role === 'user' ? 'You: ' : 'AI: '}</strong>
              {msg.text}
            </div>
          ))}
          {isChatLoading && <div className={styles['ai-msg']}>AI is thinking...</div>}
        </div>
        
        <form onSubmit={handleChat} className={styles['chat-input-area']}>
          <input
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Mera konsa kaam baki hai?"
          />
          <button type="submit" disabled={isChatLoading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
