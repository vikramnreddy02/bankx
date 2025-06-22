import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import '../App.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const nav = useNavigate();

  const call = async (path) => {
    try {
      const { data } = await api.post(`/user/${path}`, { email, password });
      setMsg(JSON.stringify(data));
      if (path === 'login') nav('/dashboard', { state: { email } });
    } catch (e) {
      setMsg(e.response?.data?.detail ?? e.message);
    }
  };

  return (
    <div className="card">
      <h2>BankX Auth</h2>
      <input placeholder="Email"    value={email}
             onChange={e => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" value={password}
             onChange={e => setPassword(e.target.value)} />
      <div className="btn-row">
        <button onClick={() => call('register')}>Register</button>
        <button onClick={() => call('login')}>Login</button>
      </div>
      <pre>{msg}</pre>
    </div>
  );
}

