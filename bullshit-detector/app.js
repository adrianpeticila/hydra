document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scanBtn');
    const copyInput = document.getElementById('copyInput');
    const resultSection = document.getElementById('resultSection');
    const scoreText = document.getElementById('scoreText');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreVerdict = document.getElementById('scoreVerdict');
    const highlightedCopy = document.getElementById('highlightedCopy');
    const sbAdvice = document.getElementById('sbAdvice');

    const bsDictionary = [
        'synergize', 'synergy', 'leverage', 'seamless', 'seamlessly', 'paradigm', 
        'paradigm shift', 'next-gen', 'next generation', 'empower', 'empowering', 
        'disrupt', 'disruptive', 'innovative', 'cutting-edge', 'bleeding-edge', 
        'scalable', 'robust', 'holistic', 'end-to-end', 'best-in-class', 
        'state-of-the-art', 'actionable', 'impactful', 'bandwidth', 'ideate',
        'growth hacking', 'thought leadership', 'value-add', 'transformational',
        'AI-driven', 'data-driven', 'agile', 'future-proof', 'omnichannel'
    ];

    const bsRegex = new RegExp(`\\b(${bsDictionary.join('|')})\\b`, 'gi');

    scanBtn.addEventListener('click', async () => {
        const text = copyInput.value.trim();
        if (!text) return;

        // Reset UI
        scanBtn.querySelector('.btn-text').textContent = 'Scanning...';
        scanBtn.disabled = true;

        setTimeout(async () => {
            analyzeCopy(text);
            
            scanBtn.querySelector('.btn-text').textContent = 'Scan Again';
            scanBtn.disabled = false;
            resultSection.classList.remove('hidden');
            
            // Scroll to results
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 600); // Fake latency for UX
    });

    function analyzeCopy(text) {
        let bsCount = 0;
        
        // Highlight text
        const highlightedHTML = text.replace(bsRegex, (match) => {
            bsCount++;
            return `<span class="bs-word">${match}</span>`;
        });
        
        highlightedCopy.innerHTML = highlightedHTML;

        // Calculate Score (0-100, higher = more bullshit)
        const wordCount = text.split(/\s+/).length;
        // Formula: % of bullshit words * 5 (so 20% bullshit is 100 score)
        let score = Math.min(100, Math.round((bsCount / Math.max(1, wordCount)) * 500));
        
        // At least 1 bs word gives some score
        if (bsCount > 0 && score < 10) score = 15 + (bsCount * 5);
        if (bsCount === 0) score = 0;
        
        animateScore(score);
        setVerdict(score);
        generateAdvice(text, bsCount);
    }

    function animateScore(targetScore) {
        let currentScore = 0;
        const duration = 1000;
        const steps = 60;
        const stepTime = duration / steps;
        
        const color = targetScore > 70 ? '#D42020' : targetScore > 30 ? '#e6a817' : '#2e8b57';
        scoreCircle.style.stroke = color;
        
        const timer = setInterval(() => {
            currentScore += Math.max(1, Math.round(targetScore / steps));
            if (currentScore >= targetScore) {
                currentScore = targetScore;
                clearInterval(timer);
            }
            scoreText.textContent = `${currentScore}%`;
            scoreCircle.setAttribute('stroke-dasharray', `${currentScore}, 100`);
        }, stepTime);
    }

    function setVerdict(score) {
        if (score === 0) {
            scoreVerdict.textContent = "Clean. Human-readable.";
            scoreVerdict.style.color = "#2e8b57";
        } else if (score < 30) {
            scoreVerdict.textContent = "Slightly corporate, but acceptable.";
            scoreVerdict.style.color = "#e6a817";
        } else if (score < 70) {
            scoreVerdict.textContent = "Heavy jargon. You are selling the drill.";
            scoreVerdict.style.color = "#D42020";
        } else {
            scoreVerdict.textContent = "Pure B2B Bullshit. Nobody understands this.";
            scoreVerdict.style.color = "#D42020";
        }
    }

    async function generateAdvice(text, bsCount) {
        if (bsCount === 0) {
            sbAdvice.textContent = "You survived the bullshit filter. Just make sure your H1 directly answers: 'What pain do you kill?'";
            return;
        }

        sbAdvice.textContent = "Generating StoryBrand fix...";

        // Try window.ai (Gemini Nano) if available in browser
        if (window.ai) {
            try {
                const session = await window.ai.createTextSession();
                const prompt = `Rewrite the following marketing copy to be simple, human, and direct. Remove all corporate jargon and buzzwords. Focus on the customer's pain and how this solves it. Do not use words like synergize, leverage, next-gen. Copy: "${text}"`;
                const stream = session.promptStreaming(prompt);
                sbAdvice.textContent = "";
                for await (const chunk of stream) {
                    sbAdvice.textContent = chunk;
                }
                return;
            } catch (e) {
                console.log("Window.ai failed or not ready", e);
            }
        }

        // Fallback generic heuristic advice
        sbAdvice.innerHTML = `
            You used <strong>${bsCount}</strong> corporate buzzwords. Your customer is not a "paradigm". They are a human with a problem.<br><br>
            <strong>The Fix:</strong><br>
            1. <em>Hero Headline (H1):</em> What exactly do you do in 5 words? (e.g. "We save you 3 hours a day")<br>
            2. <em>Subheadline:</em> What pain do you eliminate and how? Drop the adjectives.<br>
            3. <em>CTA:</em> Tell them exactly what happens when they click.
        `;
    }
});
