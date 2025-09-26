const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, { cors: { origin: '*' } });

app.use(cors());
app.use(express.json());

// Attach io to req for routes
app.use((req, res, next) => {
  req.io = io;
  next();
});

// Routes
app.use('/api', require('./routes/detection'));
app.use('/api', require('./routes/logs'));
app.use('/api', require('./routes/patterns'));

// Health check
app.get('/health', (req, res) => res.json({ status: 'OK' }));

const PORT = 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));