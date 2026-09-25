Project Delivery Risk Navigator MCP
A learning-focused MCP server that helps an AI host analyze synthetic project delivery data and identify projects requiring management attention.

Prototype status: This is a production-pattern prototype for learning and demonstration. It is not production-ready and must not use Deloitte, client, personal, or otherwise confidential data.

Purpose
The Project Delivery Risk Navigator exposes project-health capabilities through the Model Context Protocol (MCP). A connected AI host can use the server to summarize portfolio health, analyze an individual project, and identify the projects with the greatest delivery risk.

The project is intentionally small enough to build in one day while demonstrating important enterprise patterns:

Clear separation between MCP integration and business logic
Deterministic, explainable risk scoring
Read-only tools
Structured responses
Automated tests
Local development through stdio
Remote deployment through Streamable HTTP as a later step
Demonstration questions
A connected AI host should be able to answer questions such as:

Which projects need immediate attention?
Why is Project Atlas high risk?
What evidence supports the risk rating?
What actions should the delivery manager consider?
Can you prepare an executive summary of portfolio risks?
Architecture

Plain text



For a future remote deployment:


Plain text



Project structure

Plain text



MCP capabilities
Tools
Tool	Purpose	Access type
get_portfolio_overview	Summarizes overall project health	Read-only
analyze_project_risk	Calculates risk and supporting evidence for one project	Read-only
find_projects_needing_attention	Identifies projects requiring management attention	Read-only
Resource
Resource	Purpose
project://portfolio/summary	Provides a read-only portfolio summary for context
Prompt
Prompt	Purpose
executive_risk_brief	Guides preparation of a concise executive risk summary
Risk-scoring approach
The risk engine uses synthetic project indicators such as:

Schedule variance
Budget variance
Open risks
Critical issues
Resource capacity
Milestone status
The score is deterministic and explainable. Each result should include:

Numeric risk score
Green, Amber, or Red rating
Evidence supporting the rating
Potential business impact
Recommended next action
Data-quality or confidence note where appropriate
This scoring model is for demonstration only. It is not a Deloitte methodology, client-approved model, or delivery governance standard.

Local development
Prerequisites
Python 3.11 or newer
Visual Studio Code
GitHub Copilot or another approved coding assistant
An MCP-compatible local client for testing
Create a virtual environment

Bash



Activate the environment using the command appropriate for your operating system, then install the dependencies:


Bash



Run locally
The initial implementation will run through stdio, allowing a local MCP client to start the server as a process. The exact command will be documented after src/server.py is implemented.

Testing
Run the automated tests with:


Bash



pytest
Tests should focus first on the risk engine because it contains the core business logic and should work independently of MCP transport, Copilot Studio, and Azure.

Security and data boundaries
This prototype should:

Use synthetic data only
Avoid secrets in source code
Avoid logging access tokens or sensitive values
Keep capabilities read-only
Validate tool inputs
Return controlled error messages
Separate business logic from transport logic
Add HTTPS and authentication before remote exposure
For a remote deployment, additional controls will be needed, including identity and access management, OAuth or Microsoft Entra ID integration, scope or role checks, secret management, audit logging, rate limiting, monitoring, and security review.

Remote deployment direction
The target deployment pattern is:


Plain text



The server will first be developed and tested locally. Only after the local tools and tests work should the project be containerized and deployed remotely.

Remote deployment is not automatically compliant or production-ready. Compliance depends on the organization’s approved architecture, security controls, data classification, configuration, testing, and review process.

One-day delivery plan
Create the project structure and synthetic data.
Implement and test the deterministic risk engine.
Expose the risk engine through MCP tools.
Add the resource and executive-risk prompt.
Test locally through stdio.
Add Streamable HTTP support.
Containerize the server.
Deploy to Azure Container Apps if time permits.
Demonstrate the result with a small set of executive questions.
Limitations and next steps
This prototype does not include:

Real enterprise data
Write, delete, approval, or transaction tools
A production database
Full enterprise identity integration
Production monitoring and incident response
Formal security, privacy, legal, or compliance approval
Potential next steps include connecting to an approved project-data API, adding enterprise identity, implementing authorization by role or scope, adding observability, and completing the required architecture and security reviews.