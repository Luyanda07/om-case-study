import { createBackendModule } from '@backstage/backend-plugin-api';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node';
import { myCustomAction } from './myCustomAction';

export const scaffolderModuleCustomActions = createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'custom-actions',
  register(env) {
    env.registerInit({
      deps: {
        scaffolder: scaffolderActionsExtensionPoint,
      },
      async init({ scaffolder }) {
        scaffolder.addActions(myCustomAction);
      },
    });
  },
});

export default scaffolderModuleCustomActions;