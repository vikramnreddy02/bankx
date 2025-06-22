import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { api } from '../api/client';
import '../App.css';

export default function Dashboard() {
  const { state } = useLocation();
  const email = state?.email ?? 'user@example.com';
  const username = email.split('@')[0];

  const [showCreate, setShowCreate] = useState(false);
  const [initialBalance, setInitialBalance] = useState('1000');
  const [depositAmount, setDepositAmount] = useState('');
  const [recipient, setRecipient] = useState('');
  const [sendAmount, setSendAmount] = useState('');
  const [message, setMessage] = useState('');
  const [transactions, setTransactions] = useState([]);

  const toggleCreate = () => setShowCreate(!showCreate);

  const createAccount = async () => {
    try {
      await api.post('/account/create', {
        email,
        initial_balance: parseFloat(initialBalance),
      });
      setMessage(`✅ Account created with ₹${initialBalance}`);
    } catch (e) {
      setMessage(`❌ ${e.response?.data?.detail ?? e.message}`);
    }
  };

  const deposit = async () => {
    try {
      await api.post('/account/deposit', {
        email,
        amount: parseFloat(depositAmount),
      });
      setMessage(`✅ Deposited ₹${depositAmount}`);
    } catch (e) {
      setMessage(`❌ ${e.response?.data?.detail ?? e.message}`);
    }
  };

  const getBalance = async () => {
    try {
      const { data } = await api.get(`/account/balance/${email}`);
      setMessage(`💼 Current Balance: ₹${data.balance}`);
    } catch (e) {
      setMessage(`❌ ${e.response?.data?.detail ?? e.message}`);
    }
  };

  const sendMoney = async () => {
    try {
      const { data } = await api.post('/transaction/', {
        sender_email: email,
        receiver_email: recipient,
        amount: parseFloat(sendAmount),
      });
      setMessage(`✅ Sent ₹${sendAmount} to ${recipient} (Txn ID: ${data.id})`);
      fetchTransactions();
    } catch (e) {
      setMessage(`❌ ${e.response?.data?.detail ?? e.message}`);
    }
  };

  const fetchTransactions = async () => {
    try {
      // Changed 10 to 5 here:
      const { data } = await api.get(`/transaction/recent/${email}`);
      setTransactions(data.slice(0, 5)); // <--- CHANGED THIS LINE
    } catch (e) {
      console.error('Failed to fetch transactions:', e.message);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div className="card">
      <h2>🏦 Welcome, {username}</h2>

      <h3>
        <button onClick={toggleCreate}>
          {showCreate ? '❌ Hide Create Account' : '🆕 Create New Account'}
        </button>
      </h3>

      {showCreate && (
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="number"
            placeholder="Initial Balance (₹)"
            value={initialBalance}
            onChange={(e) => setInitialBalance(e.target.value)}
          />
          <button onClick={createAccount}>Create Account</button>
        </div>
      )}

      <h3>💰 Account Actions</h3>
      <div>
        <input
          type="number"
          placeholder="Amount to deposit"
          value={depositAmount}
          onChange={(e) => setDepositAmount(e.target.value)}
        />
        <button onClick={deposit}>Deposit</button>
      </div>

      <button style={{ marginTop: '1rem' }} onClick={getBalance}>
        Check Balance
      </button>

      <h3 style={{ marginTop: '2rem' }}>💸 Send Money</h3>
      <div>
        <input
          type="email"
          placeholder="Recipient Email"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
        />
        <input
          type="number"
          placeholder="Amount to Send"
          value={sendAmount}
          onChange={(e) => setSendAmount(e.target.value)}
        />
        <button onClick={sendMoney}>Send Money</button>
      </div>

      {/* ✅ Status Message */}
      {message && (
        <pre
          style={{
            backgroundColor: '#f4f4f4',
            padding: '0.75rem',
            marginTop: '2rem',
            borderLeft: '4px solid #ccc',
          }}
        >
          {message}
        </pre>
      )}
      <h3 style={{ marginTop: '2rem' }}>📄 Recent Transactions</h3>

      {transactions.length === 0 ? (
        <p>No transactions yet.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            minWidth: '500px',
            borderCollapse: 'collapse',
            marginTop: '0.5rem',
            fontSize: '0.95rem'
          }}>
            <thead>
              <tr style={{
                backgroundColor: '#f2f4f8',
                textAlign: 'left',
                borderBottom: '2px solid #ccc'
              }}>
                <th style={{ padding: '0.5rem' }}>Txn ID</th>
                <th style={{ padding: '0.5rem' }}>From</th>
                <th style={{ padding: '0.5rem' }}>To</th>
                <th style={{ padding: '0.5rem' }}>Amount</th>
                <th style={{ padding: '0.5rem' }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn) => (
                <tr key={txn.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '0.5rem' }}>{txn.id}</td>
                  <td style={{ padding: '0.5rem' }}>{txn.sender_email}</td>
                  <td style={{ padding: '0.5rem' }}>{txn.receiver_email}</td>
                  <td style={{ padding: '0.5rem' }}>₹{txn.amount}</td>
                  <td style={{ padding: '0.5rem' }}>
                    {new Date(txn.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
