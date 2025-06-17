// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const postBtn = document.getElementById('post-btn');
    const clearBtn = document.getElementById('clear-btn');
    const threadInput = document.getElementById('thread-input');
    const logOutput = document.getElementById('log-output');
    const spinner = document.getElementById('spinner');

    // --- Event Listener for the "Post Thread" button ---
    postBtn.addEventListener('click', async () => {
        const threadText = threadInput.value;

        if (!threadText.trim()) {
            logOutput.textContent = 'Error: Text area is empty.';
            return;
        }

        // Disable button and show spinner for good UX
        postBtn.disabled = true;
        spinner.classList.remove('hidden');
        logOutput.textContent = 'Connecting to the back-end...';

        try {
            const response = await fetch('/post-thread', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ thread_text: threadText }),
            });

            const result = await response.json();

            // Display the log from the back-end
            let logText = result.log.join('\n');
            if (logText.includes('403 Forbidden')) {
                logText += '\n\n⚠️ It looks like your Twitter app does not have the correct permissions (OAuth1a write access). Please check your Twitter developer portal and ensure your app has write permissions and is using OAuth1a user context.';
            }
            logOutput.textContent = logText;

        } catch (error) {
            logOutput.textContent = `A front-end error occurred: ${error.message}`;
        } finally {
            // Re-enable button and hide spinner
            postBtn.disabled = false;
            spinner.classList.add('hidden');
        }
    });

    // --- Event Listener for the "Clear" button ---
    clearBtn.addEventListener('click', () => {
        threadInput.value = '';
        logOutput.textContent = 'Awaiting input...';
    });
});