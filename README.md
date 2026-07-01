# Chess Project

## Running the Project

To start the application, open **three separate terminals** and run the following commands.

### 1. Start the Backend Server

Navigate to the server directory and start the FastAPI server:

```bash
cd ./server
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

### 2. Expose the Server with Ngrok

Create a public tunnel for the backend server:

```bash
ngrok http 8001
```

---

### 3. Build the Frontend

Run the frontend build process:

```bash
npm run build
```

---

After completing these steps, the chess application should be up and running.
