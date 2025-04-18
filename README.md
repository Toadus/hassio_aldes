# Home Assistant custom component for Aldes InspirAIR Top

Simple integration to allow selection of mode from Home Assistant.

Licensed under the MIT License. See LICENSE for details.

## Features

* Login in Aldes API
* Configure Home Assitant Aldes entities
* Change ventilation mode
* Configure `Holidays` mode without specifying end date
* Display ventilation metrics

## Installation on Home Assistant

### Using HACS
This is not part of the default store and has to be added as a custom repository.

Setting up a custom repository is done by:

Go into HACS from the side bar.
Click into Integrations.
Click the 3-dot menu in the top right and select Custom repositories
In the UI that opens, copy and paste the url for this github repo into the Add custom repository URL field.
Set the category to Integration.
Click the Add button.
Restart your Home Assistant and add Aldes integration in Integration section.
Use your Aldesconnect credentials to login.

### Manual installation
Download all files and copy them to "config/custom_components/aldes" folder.
Restart your Home Assistant and add Aldes integration in Integration section.
Use your Aldesconnect credentials to login.
