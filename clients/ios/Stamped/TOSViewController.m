//
//  TOSViewController.m
//  Stamped
//
//  Created by Jake Zien on 11/3/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "TOSViewController.h"

@interface TOSViewController () {
    UIView* openView_;
}
@end

static NSString* const kStampedTermsURL = @"http://www.stamped.com/terms-mobile.html";
static NSString* const kStampedPrivacyURL = @"http://www.stamped.com/privacy-mobile.html";
static NSString* const kStampedLicensesURL = @"http://www.stamped.com/licenses-mobile.html";

@implementation TOSViewController

@synthesize webView = webView_;
@synthesize contentView = contentView_;
@synthesize settingsButton = settingsButton_;
@synthesize doneButton = doneButton_;
@synthesize termsView = termsView_;
@synthesize termsWebView = termsWebView_;
@synthesize privacyView = privacyView_;
@synthesize privacyWebView = privacyWebView_;
@synthesize licensesView = licensesView_;
@synthesize licensesWebView = licensesWebView_;

- (id)initWithURL:(NSURL*)aURL {
    return [self initWithNibName:@"TOSViewController" bundle:nil];
}

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        openView_ = nil;
    }
    return self;
}

- (void)dealloc {
    self.webView = nil;
    self.contentView = nil;
    self.settingsButton = nil;
    self.doneButton = nil;
    self.termsView = nil;
    self.termsWebView = nil;
    self.privacyView = nil;
    self.privacyWebView = nil;
    self.licensesView = nil;
    self.licensesWebView = nil;
    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
    self.view.clipsToBounds = YES;
    self.webView.scalesPageToFit = YES;
    [self.webView loadRequest:[NSURLRequest requestWithURL:URL]];
    [super viewDidLoad];
    
    UITapGestureRecognizer* gr;
    gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
    [self.termsView addGestureRecognizer:gr];
    [gr release];
    gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
    [self.privacyView addGestureRecognizer:gr];
    [gr release];
    gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
    [self.licensesView addGestureRecognizer:gr];
    [gr release];
    
    for(UIView *wview in [[[termsWebView_ subviews] objectAtIndex:0] subviews]) {       // Hide webView background/shadows. Thanks to jodm.
        if([wview isKindOfClass:[UIImageView class]])                                     // http://stackoverflow.com/questions/1074320/remove-uiwebview-shadow
            wview.hidden = YES;
    }  
    for(UIView *wview in [[[privacyWebView_ subviews] objectAtIndex:0] subviews]) {
        if([wview isKindOfClass:[UIImageView class]])                              
            wview.hidden = YES;
    }  
    for(UIView *wview in [[[licensesWebView_ subviews] objectAtIndex:0] subviews]) {
        if([wview isKindOfClass:[UIImageView class]])                              
            wview.hidden = YES;
    }
    
    [termsWebView_ loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:kStampedTermsURL]]];
    [privacyWebView_ loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:kStampedPrivacyURL]]];
    [licensesWebView_ loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:kStampedLicensesURL]]];
//    
//    CGRect licenseFrame = licensesView_.frame;
//    licenseFrame.size.height = 336;
//    licensesView_.frame = licenseFrame;
//    licensesWebView_.scrollView.contentSize = CGSizeMake(licensesWebView_.scrollView.contentSize.width, 3000);
//    NSLog(@"licenses:%f,%f,%d", licensesWebView_.scrollView.contentSize.height, licensesWebView_.scrollView.frame.size.height, licensesWebView_.scrollView.scrollEnabled);
//    
    openView_ = termsView_;
}

- (void)viewDidUnload {
    self.webView = nil;
    self.contentView = nil;
    self.settingsButton = nil;
    self.doneButton = nil;
    self.termsView = nil;
    self.termsWebView = nil;
    self.privacyView = nil;
    self.privacyWebView = nil;
    self.licensesView = nil;
    self.licensesWebView = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.navigationController setNavigationBarHidden:YES animated:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
    [self.navigationController setNavigationBarHidden:NO animated:animated];
    [super viewWillDisappear:animated];
}

- (IBAction)done:(id)sender {
    UIViewController* vc = nil;
    if ([self respondsToSelector:@selector(presentingViewController)])
        vc = [(id)self presentingViewController];
    else
        vc = self.parentViewController;
    [vc dismissModalViewControllerAnimated:YES];
}

- (IBAction)settingsButtonPressed:(id)sender {
    [self.navigationController popViewControllerAnimated:YES];
}

- (void)handleTap:(id)sender {
    CGFloat delta = 300;
    CGFloat privacyCollapsed = 40;
    CGFloat privacyExpanded = privacyCollapsed + delta;
    CGFloat licenseCollapsed = 80;
    CGFloat licenseExpanded = licenseCollapsed + delta;
    [UIView animateWithDuration:0.25
                          delay:0
                        options:UIViewAnimationCurveEaseInOut
                     animations:^{
                         if ([((UITapGestureRecognizer*)sender).view isEqual:openView_])
                             return;
                         if ([((UITapGestureRecognizer*)sender).view isEqual:termsView_]) {
                             CGRect privacyFrame = privacyView_.frame;
                             privacyFrame.origin.y = privacyExpanded;
                             privacyView_.frame = privacyFrame;
                             CGRect licenseFrame = licensesView_.frame;
                             licenseFrame.origin.y = licenseExpanded;
                             licensesView_.frame = licenseFrame;
                             openView_ = termsView_;
                         }
                         else if ([((UITapGestureRecognizer*)sender).view isEqual:privacyView_]) {
                             CGRect privacyFrame = privacyView_.frame;
                             privacyFrame.origin.y = privacyCollapsed;
                             privacyView_.frame = privacyFrame;
                             CGRect licenseFrame = licensesView_.frame;
                             licenseFrame.origin.y = licenseExpanded;
                             licensesView_.frame = licenseFrame;
                             openView_ = privacyView_;
                         }
                         else if ([((UITapGestureRecognizer*)sender).view isEqual:licensesView_]) {
                             CGRect privacyFrame = privacyView_.frame;
                             privacyFrame.origin.y = privacyCollapsed;
                             privacyView_.frame = privacyFrame;
                             CGRect licenseFrame = licensesView_.frame;
                             licenseFrame.origin.y = licenseCollapsed;
                             licensesView_.frame = licenseFrame;
                             openView_ = licensesView_;
                         }
                         
                     }
                     completion:nil];
}

@end
