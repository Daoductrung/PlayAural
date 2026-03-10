import os
import glob
import re

def main():
    game_files = glob.glob("server/games/*/game.py")

    for filepath in game_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Update the method signature safely using regex to handle different spacings/linebreaks
        content = re.sub(
            r'def create_player\(\s*self,\s*player_id:\s*str,\s*name:\s*str,\s*is_bot:\s*bool\s*=\s*False\s*\)([^:]*):',
            r'def create_player(self, player_id: str, name: str, is_bot: bool = False, display_name: str = "")\1:',
            content
        )

        parts = content.split('def create_player(')
        if len(parts) == 2:
            before = parts[0]
            after = parts[1]

            def replacer(match):
                if match.group(1) == ')':
                    return 'is_bot=is_bot, display_name=display_name)'
                else:
                    return 'is_bot=is_bot, display_name=display_name,'

            # Only do the replacement if it hasn't been done yet in this method block
            if "display_name=display_name" not in after.split('def ')[0]:
                after = re.sub(r'is_bot=is_bot\s*([,)])', replacer, after, count=1)

            content = before + 'def create_player(' + after

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    main()
