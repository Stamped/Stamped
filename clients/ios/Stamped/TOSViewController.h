//
//  TOSViewController.h
//  Stamped
//
//  Created by Jake Zien on 11/3/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "CollapsibleViewController.h"

@interface TOSViewController : UIViewController {
  NSURL* URL;
}

@property (nonatomic, retain) IBOutlet UIWebView* webView;
@property (nonatomic, retain) IBOutlet UIView* contentView;
@property (nonatomic, retain) IBOutlet UIButton* settingsButton;
@property (nonatomic, retain) IBOutlet UIButton* doneButton;
@property (nonatomic, retain) IBOutlet UIView* termsView;
@property (nonatomic, retain) IBOutlet UIWebView* termsWebView;
@property (nonatomic, retain) IBOutlet UIView* privacyView;
@property (nonatomic, retain) IBOutlet UIWebView* privacyWebView;
@property (nonatomic, retain) IBOutlet UIView* licensesView;
@property (nonatomic, retain) IBOutlet UIWebView* licensesWebView;

- (id)initWithURL:(NSURL*)aURL;
- (IBAction)done:(id)sender;
- (IBAction)settingsButtonPressed:(id)sender;
- (void)handleTap:(id)sender;

@end
