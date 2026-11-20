import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import fs from 'node:fs/promises';
import path from 'node:path';

export const myCustomAction = createTemplateAction({
  id: 'my:custom:action',
  description: 'Creates a new file in the template workspace',
  schema: {
    input: {
      filename: (z) =>
        z.string().describe('Name of the file to create'),
      content: (z) =>
        z.string().describe('Content to write into the file'),
    },
  },
  async handler(ctx) {
    const filePath = path.join(ctx.workspacePath, ctx.input.filename);

    await fs.writeFile(filePath, ctx.input.content, 'utf8');
  },
});