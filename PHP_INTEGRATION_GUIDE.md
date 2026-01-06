# PHP Integration Guide - Quiz Generator API

Simple guide for integrating the Quiz Generator API with PHP applications.

---

## Base URL

```
Production: https://ai-quiz-generator-f8dr.onrender.com
Local: http://localhost:8000
```

---

## Main Endpoint

### Generate Quiz

**POST** `/api/generate-quiz`

Generates a quiz from a URL, uploaded file, or video URL.

---

## Basic PHP Integration

### 1. Generate Quiz from URL

```php
<?php

// API endpoint
$apiUrl = 'https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz';

// Prepare data
$data = [
    'url' => 'https://en.wikipedia.org/wiki/Artificial_intelligence',
    'age_mode' => '18+'  // or 'kids' for under-18
];

// Initialize cURL
$ch = curl_init($apiUrl);

// Set cURL options
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 120); // 2 minute timeout

// Execute request
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

// Close connection
curl_close($ch);

// Handle response
if ($httpCode == 200) {
    $result = json_decode($response, true);

    // Success - display quiz
    echo "Quiz Title: " . $result['content']['title'] . "\n";
    echo "Number of Questions: " . $result['quiz']['num_quiz_questions'] . "\n";

    // Loop through questions
    foreach ($result['quiz']['questions'] as $index => $question) {
        echo "\nQ" . ($index + 1) . ": " . $question['question'] . "\n";

        foreach ($question['options'] as $key => $option) {
            echo "  " . $key . ") " . $option . "\n";
        }
    }
} else {
    // Error handling
    $error = json_decode($response, true);
    echo "Error: " . $error['detail']['detail'] . "\n";
}

?>
```

---

### 2. Generate Quiz from Video URL (YouTube)

```php
<?php

$apiUrl = 'https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz';

$data = [
    'video_url' => 'https://www.youtube.com/watch?v=example',
    'age_mode' => 'kids'
];

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 300); // 5 minute timeout for videos

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);

// Display results
print_r($result);

?>
```

---

### 3. Upload File (PDF, DOCX, TXT)

```php
<?php

$apiUrl = 'https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz';

// File path
$filePath = '/path/to/your/document.pdf';

// Create CURLFile object
$cfile = new CURLFile($filePath, mime_content_type($filePath), basename($filePath));

// Prepare POST data
$data = [
    'file' => $cfile,
    'age_mode' => '18+'
];

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 120);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
print_r($result);

?>
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | No* | Web URL to generate quiz from |
| `video_url` | string | No* | YouTube/video URL |
| `file` | file | No* | Uploaded file (PDF, DOCX, TXT) |
| `age_mode` | string | No | `"kids"` or `"18+"` (default: `"18+"`) |

*One of `url`, `video_url`, or `file` is required.

---

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "job_id": "abc123...",
  "content": {
    "title": "Artificial Intelligence Overview",
    "description": "Brief summary...",
    "categories": ["Technology", "AI"]
  },
  "quiz": {
    "num_quiz_questions": 5,
    "questions": [
      {
        "question": "What is AI?",
        "options": {
          "a": "Answer 1",
          "b": "Answer 2",
          "c": "Answer 3",
          "d": "Answer 4"
        },
        "correct_answer": "a",
        "difficulty": "easy",
        "weights": {
          "a": 0.8,
          "b": 0.6,
          "c": 0.4,
          "d": 0.2
        }
      }
    ]
  },
  "points_awarded": 100,
  "generated_at": "2025-01-07T12:00:00Z"
}
```

### Error Response (400/403/500)

```json
{
  "detail": {
    "success": false,
    "detail": "Error message here"
  }
}
```

---

## Complete PHP Class Example

```php
<?php

class QuizGeneratorAPI {
    private $apiUrl;
    private $timeout;

    public function __construct($apiUrl = 'https://ai-quiz-generator-f8dr.onrender.com') {
        $this->apiUrl = $apiUrl;
        $this->timeout = 120;
    }

    /**
     * Generate quiz from URL
     */
    public function generateFromUrl($url, $ageMode = '18+') {
        $data = [
            'url' => $url,
            'age_mode' => $ageMode
        ];

        return $this->makeRequest($data);
    }

    /**
     * Generate quiz from video URL
     */
    public function generateFromVideo($videoUrl, $ageMode = '18+') {
        $data = [
            'video_url' => $videoUrl,
            'age_mode' => $ageMode
        ];

        $this->timeout = 300; // 5 minutes for videos
        return $this->makeRequest($data);
    }

    /**
     * Generate quiz from file
     */
    public function generateFromFile($filePath, $ageMode = '18+') {
        if (!file_exists($filePath)) {
            throw new Exception("File not found: $filePath");
        }

        $cfile = new CURLFile($filePath, mime_content_type($filePath), basename($filePath));

        $data = [
            'file' => $cfile,
            'age_mode' => $ageMode
        ];

        return $this->makeRequest($data, true);
    }

    /**
     * Make API request
     */
    private function makeRequest($data, $isFileUpload = false) {
        $ch = curl_init($this->apiUrl . '/api/generate-quiz');

        curl_setopt($ch, CURLOPT_POST, true);

        if ($isFileUpload) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        } else {
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
        }

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);

        curl_close($ch);

        if ($error) {
            throw new Exception("cURL Error: $error");
        }

        $result = json_decode($response, true);

        if ($httpCode != 200) {
            throw new Exception("API Error: " . ($result['detail']['detail'] ?? 'Unknown error'));
        }

        return $result;
    }
}

// Usage Example
$api = new QuizGeneratorAPI();

try {
    // Generate from URL
    $quiz = $api->generateFromUrl('https://en.wikipedia.org/wiki/Python_(programming_language)');

    echo "Title: " . $quiz['content']['title'] . "\n";
    echo "Questions: " . $quiz['quiz']['num_quiz_questions'] . "\n";

    foreach ($quiz['quiz']['questions'] as $i => $q) {
        echo "\nQ" . ($i+1) . ": " . $q['question'] . "\n";
        foreach ($q['options'] as $key => $opt) {
            $marker = ($key == $q['correct_answer']) ? '✓' : ' ';
            echo "  [$marker] $key) $opt\n";
        }
    }

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

?>
```

---

## Error Handling

```php
<?php

try {
    $api = new QuizGeneratorAPI();
    $quiz = $api->generateFromUrl($url);

    // Success
    processQuiz($quiz);

} catch (Exception $e) {
    // Handle specific errors
    $message = $e->getMessage();

    if (strpos($message, '403') !== false) {
        echo "Content blocked or site has bot protection";
    } elseif (strpos($message, '400') !== false) {
        echo "Invalid input or content too short";
    } elseif (strpos($message, 'timeout') !== false) {
        echo "Request timed out - try again";
    } else {
        echo "Error: " . $message;
    }
}

?>
```

---

## Testing

### Health Check

```php
<?php

$healthUrl = 'https://ai-quiz-generator-f8dr.onrender.com/health';

$response = file_get_contents($healthUrl);
$status = json_decode($response, true);

if ($status['status'] === 'healthy') {
    echo "API is healthy\n";
} else {
    echo "API is down\n";
}

?>
```

---

## Tips

1. **Timeouts**: Set appropriate timeouts
   - URLs: 120 seconds
   - Videos: 300 seconds (5 minutes)
   - Files: 120 seconds

2. **Error Handling**: Always wrap API calls in try-catch

3. **Age Mode**: Use `"kids"` for strict content filtering

4. **File Size**: Keep uploaded files under 10MB for best performance

5. **Caching**: Cache quiz results to avoid repeated API calls

---

## Support

For issues or questions:
- GitHub: https://github.com/shubh1996/ai-quiz-generator/issues
- API Docs: See `API_SPECIFICATION.md` for full details
