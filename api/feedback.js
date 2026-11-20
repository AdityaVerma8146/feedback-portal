let feedbackItems = [
  {
    feedbackId: "seed-1",
    name: "Aditya Verma",
    email: "aditya@example.com",
    rating: 5,
    message: "Feedback portal is live on Vercel and ready for testing!",
    createdAt: Math.floor(Date.now() / 1000) - 1800
  },
  {
    feedbackId: "seed-2",
    name: "Student Reviewer",
    email: "student@example.com",
    rating: 5,
    message: "Clean, responsive design and lightning fast feedback submission.",
    createdAt: Math.floor(Date.now() / 1000) - 7200
  }
];

export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method === "GET") {
    return res.status(200).json({ items: feedbackItems });
  }

  if (req.method === "POST") {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const { name, email, rating, message } = body || {};

    if (!name || !email || !message) {
      return res.status(400).json({ error: "Name, email, and message are required." });
    }

    const newItem = {
      feedbackId: "fb-" + Date.now(),
      name: String(name).slice(0, 80),
      email: String(email).slice(0, 120),
      rating: parseInt(rating) || 5,
      message: String(message).slice(0, 1000),
      createdAt: Math.floor(Date.now() / 1000)
    };

    feedbackItems.unshift(newItem);
    return res.status(201).json({
      message: "Thank you! Feedback saved successfully.",
      feedbackId: newItem.feedbackId
    });
  }

  return res.status(405).json({ error: "Method not allowed" });
}
