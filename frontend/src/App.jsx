import { useState } from 'react';

const players = [
  'Sinner',
  'Alcaraz',
  'Djokovic',
  'Zverev',
  'Fritz',
  'Nadal',
  'Medvedev',
  'Rune',
  'Rublev',
  'Tsitsipas',
];

function App() {
  const [form, setForm] = useState({
    player1: 'Sinner',
    player2: 'Alcaraz',
    surface: 'Hard',
    round: 'Final',
    rank1: 1,
    rank2: 2,
    pts1: 12000,
    pts2: 9800,
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  async function predictWinner() {
    if (form.player1 === form.player2) {
      setError('Choose two different players.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...form,
          rank1: Number(form.rank1),
          rank2: Number(form.rank2),
          pts1: Number(form.pts1),
          pts2: Number(form.pts2),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Prediction failed.');
      }

      setPrediction(data.winner);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: '40px auto', padding: 24, fontFamily: 'sans-serif' }}>
      <h1>Tennis Match Predictor</h1>
      <h2>{form.player1} vs {form.player2}</h2>

      <div style={{ display: 'grid', gap: 12 }}>
        <label>
          Player 1
          <select name="player1" value={form.player1} onChange={handleChange} style={{ width: '100%', padding: 8 }}>
            {players.map((player) => (
              <option key={player} value={player}>{player}</option>
            ))}
          </select>
        </label>

        <label>
          Player 2
          <select name="player2" value={form.player2} onChange={handleChange} style={{ width: '100%', padding: 8 }}>
            {players.map((player) => (
              <option key={player} value={player}>{player}</option>
            ))}
          </select>
        </label>

        <label>
          Surface
          <select name="surface" value={form.surface} onChange={handleChange} style={{ width: '100%', padding: 8 }}>
            <option value="Hard">Hard</option>
            <option value="Clay">Clay</option>
            <option value="Grass">Grass</option>
            <option value="Carpet">Carpet</option>
          </select>
        </label>

        <label>
          Round
          <select name="round" value={form.round} onChange={handleChange} style={{ width: '100%', padding: 8 }}>
            <option value="Final">Final</option>
            <option value="Semifinals">Semifinals</option>
            <option value="Quarterfinals">Quarterfinals</option>
            <option value="1st Round">1st Round</option>
            <option value="2nd Round">2nd Round</option>
            <option value="3rd Round">3rd Round</option>
            <option value="4th Round">4th Round</option>
          </select>
        </label>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <label>
            Rank 1
            <input type="number" name="rank1" value={form.rank1} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
          </label>

          <label>
            Rank 2
            <input type="number" name="rank2" value={form.rank2} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
          </label>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <label>
            Points 1
            <input type="number" name="pts1" value={form.pts1} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
          </label>

          <label>
            Points 2
            <input type="number" name="pts2" value={form.pts2} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
          </label>
        </div>

        <button onClick={predictWinner} disabled={loading} style={{ padding: '10px 16px', cursor: loading ? 'not-allowed' : 'pointer' }}>
          {loading ? 'Predicting...' : 'Predict Winner'}
        </button>

        {error && <p style={{ color: 'crimson', margin: 0 }}>{error}</p>}
        {prediction && <h3>Predicted Winner: {prediction}</h3>}
      </div>
    </div>
  );
}

export default App;