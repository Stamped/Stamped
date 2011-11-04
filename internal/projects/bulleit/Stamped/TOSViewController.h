//
//  TOSViewController.h
//  Stamped
//
//  Created by Jake Zien on 11/3/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface TOSViewController : UIViewController {
  NSURL* URL;
}

@property (nonatomic, retain) IBOutlet UIWebView* webView;
@property (nonatomic, retain) IBOutlet UIButton* settingsButton;
@property (nonatomic, retain) IBOutlet UIButton* doneButton;

-(id)initWithURL:(NSURL*)aURL;
-(IBAction)done:(id)sender;
-(IBAction)settingsButtonPressed:(id)sender;

@end
