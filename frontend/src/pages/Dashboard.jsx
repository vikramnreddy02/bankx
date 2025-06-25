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
      setMessage(`Current Balance: ₹${data.balance}`);
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
      setMessage(`Sent ₹${sendAmount} to ${recipient} (Txn ID: ${data.id})`);
      fetchTransactions();
    } catch (e) {
      setMessage(`❌ ${e.response?.data?.detail ?? e.message}`);
    }
  };

  const fetchTransactions = async () => {
    try {
      const { data } = await api.get(`/transaction/recent/${email}`);
      setTransactions(data.slice(0, 5));
    } catch (e) {
      console.error('Failed to fetch transactions:', e.message);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div className="dashboard-container">
      <h2 className="welcome-text">Welcome, {username}</h2>

{/* Create Account */}
<div className="card-section">
  <div className="section-header">
    <h3>Create New Account</h3>
    <button className="disclosure-button" onClick={toggleCreate}>
      {showCreate ? 'Hide' : 'Show'}
    </button>
  </div>

  {showCreate && (
    <div className="form-group vertical">
      <label htmlFor="initial-balance">Initial Deposit (₹)</label>
      <input
        id="initial-balance"
        type="number"
        placeholder="e.g. 1000"
        value={initialBalance}
        onChange={(e) => setInitialBalance(e.target.value)}
      />
      <button onClick={createAccount}>Create Account</button>
    </div>
  )}
</div>

      {/* Deposit & Balance */}
      <div className="card-section">
        <h3>Deposit & Balance</h3>
        <div className="form-group">
          <input
            type="number"
            placeholder="Amount to deposit"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
          />
          <button onClick={deposit}>Deposit</button>
          <button onClick={getBalance} style={{ marginLeft: '1rem' }}>
            Check Balance
          </button>
        </div>
      </div>

      {/* Send Money */}
      <div className="card-section">
        <h3>Send Money</h3>
        <div className="form-group">
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
      </div>

      {/* Status Message */}
      {message && (
        <div className="card-section">
          <div
            className={`status-message ${
              message.startsWith('✅') ? 'success' :
              message.startsWith('❌') ? 'error' : 'info'
            }`}
          >
            {message}
          </div>
        </div>
      )}

      {/* Transactions */}
      <div className="card-section">
        <h3>Recent Transactions</h3>
        {transactions.length === 0 ? (
          <p>No transactions yet.</p>
        ) : (
          <div className="table-container">
            <table className="txn-table">
              <thead>
                <tr>
                  <th>Txn ID</th>
                  <th>From</th>
                  <th>To</th>
                  <th>Amount</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr key={txn.id}>
                    <td>{txn.id}</td>
                    <td>{txn.sender_email}</td>
                    <td>{txn.receiver_email}</td>
                    <td>₹{txn.amount}</td>
                    <td>{new Date(txn.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

