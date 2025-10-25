from shared.notion_config import NotionConfig, NotionConfigurationError


class AgentCore:
    def __init__(self, notion_config: NotionConfig | None = None):
        try:
            self.notion_config = notion_config or NotionConfig.from_env()
        except NotionConfigurationError:
            # Re-raise to preserve the informative message for callers/tests.
            raise

    def run(self):
        print("Agent is running")
