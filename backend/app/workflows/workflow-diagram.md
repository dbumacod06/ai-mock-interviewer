# Interview Workflow Diagram

## Graph Structure

```mermaid
graph TD
    START[START] --> transcriber[transcriber]
    transcriber --> transcription_corrector[transcription_corrector]
    transcription_corrector --> evaluate_and_route[evaluate_and_route]
    
    evaluate_and_route --> route1{next_action?}
    route1 -->|"end"| END[END]
    route1 -->|"applicant_inquiries"| applicant_inquiries_node[applicant_inquiries_node<br/>Respond to applicant's question]
    route1 -->|"evaluate_answer"| evaluate_answer_node[evaluate_answer_node<br/>First turn check + Review answer + Decide followup]
    
    evaluate_answer_node --> route2{next_action?}
    route2 -->|"generate_response"| generate_response_node[generate_response_node<br/>Phase advance + New question]
    route2 -->|None| END
    
    applicant_inquiries_node --> END
    generate_response_node --> END
```

## Node Descriptions

### evaluate_and_route
Determines the next action based on interview state:
- **end**: Returns completion message if `current_phase_index >= len(interview_phases) - 1` or if applicant indicates no more questions
- **applicant_inquiries**: Routes to applicant inquiries handler if in `applicant_inquiries` phase with questions already asked
- **evaluate_answer**: Routes to answer evaluation for normal phases (icebreaker, preliminary, technical, situational) AND first turn of applicant_inquiries

### evaluate_answer_node
Handles two scenarios:
1. **First turn of applicant_inquiries**: Returns opening message "That concludes my questions..." directly
2. **Answer evaluation**: Reviews the applicant's answer, returns followup question directly if needed, otherwise routes to `generate_response_node`

### applicant_inquiries_node
Responds to the applicant's questions about the company/role. Increments question counter and resets follow-up count.

### generate_response_node
Handles phase advancement and new question generation:
- Checks if max questions reached, advances phase
- If advanced to `applicant_inquiries`, returns first turn message
- Otherwise generates the next interview question for the current phase
