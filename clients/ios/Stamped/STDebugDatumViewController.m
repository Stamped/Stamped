//
//  STDebugDatumViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDebugDatumViewController.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import <MessageUI/MFMailComposeViewController.h>
#import "UIFont+Stamped.h"
#import "STStampedAPI.h"

@interface STDebugDatumViewController () <UITextViewDelegate, MFMailComposeViewControllerDelegate>

@property (nonatomic, readonly, retain) NSString* string;
@property (nonatomic, readonly, retain) UITextView* textView;

@end

@implementation STDebugDatumViewController

@synthesize string = string_;
@synthesize textView = textView_;

- (id)initWithString:(NSString*)string
{
  self = [super init];
  if (self) {
    string_ = [string retain];
  }
  return self;
}

- (void)dealloc
{
  [string_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  CGFloat padding = 5;
  textView_ = [[UITextView alloc] initWithFrame:CGRectMake(padding, 
                                                           padding, 
                                                           self.scrollView.frame.size.width - 2 * padding, 
                                                           self.scrollView.frame.size.height - 2 * padding- 80)];
  textView_.text = self.string;
  textView_.layer.borderWidth = 2;
  textView_.layer.borderColor = [UIColor colorWithWhite:.7 alpha:1].CGColor;
  UIView* accessoryView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)] autorelease];
  accessoryView.backgroundColor = [UIColor clearColor];
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.frame = CGRectMake(0, 1, 320, 43);
  backgroundGradient.colors = [NSArray arrayWithObjects:
                               (id)[UIColor colorWithWhite:0.15 alpha:0.95].CGColor,
                               (id)[UIColor colorWithWhite:0.30 alpha:0.95].CGColor, nil];
  [accessoryView.layer addSublayer:backgroundGradient];
  [backgroundGradient release];
  
  UIButton* doneButton = [UIButton buttonWithType:UIButtonTypeCustom];
  doneButton.frame = CGRectMake(248, 4, 69, 38);
  [doneButton setImage:[UIImage imageNamed:@"done_button"] forState:UIControlStateNormal];
  doneButton.contentMode = UIViewContentModeScaleAspectFit;
  [doneButton addTarget:self
                 action:@selector(editorDoneButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [accessoryView addSubview:doneButton];
  self.textView.inputAccessoryView = accessoryView;
  self.textView.delegate = self;
  [self.scrollView appendChildView:textView_];
  UILabel* buttonText = [Util viewWithText:@"Submit" 
                                 font:[UIFont stampedTitleFont]
                                color:[UIColor blackColor]
                                 mode:UILineBreakModeClip 
                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:buttonText withDeltas:CGRectMake(30, 0, 50, 0)];
  buttonText.layer.borderColor = [UIColor grayColor].CGColor;
  buttonText.layer.borderWidth = 2;
  buttonText.layer.cornerRadius = 5;
  buttonText.textAlignment = UITextAlignmentCenter;
  [self.scrollView appendChildView:buttonText];
  UIView* tapTarget = [Util tapViewWithFrame:buttonText.frame target:self selector:@selector(submitButtonPressed:) andMessage:nil];
  [self.scrollView addSubview:tapTarget];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [textView_ release];
}

- (void)textViewDidBeginEditing:(UITextView *)textView {
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
}

- (BOOL)textViewShouldEndEditing:(UITextView *)textView {
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
  [textView resignFirstResponder];
  return YES;
}

- (void)editorDoneButtonPressed:(id)button {
  [self.textView endEditing:YES];
}

- (void)submitButtonPressed:(id)button {
  MFMailComposeViewController* controller = [[MFMailComposeViewController alloc] init];
  controller.mailComposeDelegate = self;
  [controller setToRecipients:[NSArray arrayWithObject:@"dev@stamped.com"]];
  [controller setSubject:[NSString stringWithFormat:@"Report from %@ (%@)", 
                          STStampedAPI.sharedInstance.currentUser.name,
                          STStampedAPI.sharedInstance.currentUser.screenName]];
  [controller setMessageBody:self.textView.text isHTML:NO]; 
  if (controller) [self presentModalViewController:controller animated:YES];
  [controller release];
}

- (void)mailComposeController:(MFMailComposeViewController*)controller  
          didFinishWithResult:(MFMailComposeResult)result 
                        error:(NSError*)error;
{
  NSString* string;
  if (result == MFMailComposeResultSent) {
    string = @"Report sent";
  }
  else {
    string = @"Report failed!";
  }
  [Util warnWithMessage:string andBlock:^{
    [self dismissModalViewControllerAnimated:YES];
  }];
}

@end
