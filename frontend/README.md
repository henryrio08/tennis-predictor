# Frontend

This is the React side of the Tennis Predictor. It collects the match details, sends them to the Flask API, and shows the winner returned by the model.

## Run it

You'll need Node.js and npm. From the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Vite prints a local URL in the terminal, usually `http://localhost:5173`. The backend needs to be running too, or the page won't be able to get a prediction.

The easiest way to start both parts is to go back to the repository root and run `./run.sh`. See the main README for the full setup.

## API address

The frontend uses the backend address configured through `VITE_API_URL`. If you're running the API somewhere other than its default local address, copy `.env.example` to `.env.local`, set `VITE_API_URL` to the backend base URL, and restart Vite.

## Main files

- `src/App.jsx` contains the form and prediction result UI.
- `src/App.css` styles the app layout.
- `src/index.css` contains the global styles.
- `src/main.jsx` starts the React app.

The API and model code live in the `backend/` directory. The [code walkthrough](../docs/CODE_WALKTHROUGH.md) explains how the request moves through the app.
