import * as base from '@jupyter-widgets/base';
import { ManagerBase } from '@jupyter-widgets/base-manager';
import * as controls from '@jupyter-widgets/controls';
import { Widget as LuminoWidget } from '@lumino/widgets';


class WidgetManager extends ManagerBase {
  private el: HTMLElement;

  constructor(el: HTMLElement) {
    super();
    this.el = el;
  }

  public loadClass(className: string, moduleName: string, moduleVersion: string): Promise<any> {
    return new Promise((resolve, reject) => {
      if (moduleName === '@jupyter-widgets/controls') {
        resolve(controls);
      } else if (moduleName === '@jupyter-widgets/base') {
        resolve(base);
      } else {
        const fallback = (err: any) => {
          let failedId = err.requireModules && err.requireModules[0];
          if (failedId) {
            console.log(`Falling back to jsDelivr for ${moduleName}@${moduleVersion}`);
            (window as any).require(
              [`https://cdn.jsdelivr.net/npm/${moduleName}@${moduleVersion}/dist/index.js`],
              resolve,
              reject
            );
          } else {
            throw err;
          }
        };
        (window as any).require([`${moduleName}.js`], resolve, fallback);
      }
    }).then((module: any) => {
      if (module[className]) {
        return module[className];
      } else {
        return Promise.reject(`Class ${className} not found in module ${moduleName}@${moduleVersion}`);
      }
    });
  }

  public display_view(view: any): Promise<any> {
    return Promise.resolve(view).then((view) => {
      LuminoWidget.attach(view.luminoWidget, this.el);
      return view;
    });
  }

  protected _get_comm_info(): Promise<{}> {
    return Promise.resolve({});
  }

  protected _create_comm(): Promise<any> {
    return Promise.reject('no comms available');
  }
}

export { WidgetManager };
