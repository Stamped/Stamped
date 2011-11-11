//
//  Alerts.m
//  Stamped
//
//  Created by Jake Zien on 11/9/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "Alerts.h"

@implementation Alerts

+ (UIAlertView*)alertWithTemplate:(AlertTemplate)aTemplate delegate:(id)aDelegate {  
  switch (aTemplate) {
    case AlertTemplateDefault:
      return [[[UIAlertView alloc] initWithTitle:@"An Error Occurred"
                                   message:@"Something went wrong.\nPlease try again later."
                                   delegate:aDelegate
                                   cancelButtonTitle:@"OK"
                                   otherButtonTitles:nil] autorelease];
    case AlertTemplateNoInternet:
      return [[[UIAlertView alloc] initWithTitle:@"No Connection"
                                         message:@"Stamped is unable to connect to the internet."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateTimedOut:
      return [[[UIAlertView alloc] initWithTitle:@"Request Timed Out"
                                         message:@"Stamped couldn't connect.\nPlease try again later."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateAlreadyStamped:
      return [[[UIAlertView alloc] initWithTitle:@"Already Stamped"
                                         message:@"You can only stamp something once."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateWebViewFail:
      return [[[UIAlertView alloc] initWithTitle:@"An Error Occurred"
                                         message:@"There was a problem loading this page."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateInvalidSignup:
      return [[[UIAlertView alloc] initWithTitle:@"Registration Failed"
                                         message:@"Please check that all your information is valid."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateFieldRequired:
      return [[[UIAlertView alloc] initWithTitle:@"Information Missing"
                                         message:@"Please make sure that you've filled all required fields."
                                        delegate:aDelegate
                               cancelButtonTitle:@"OK"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateInvalidLogin:
      return [[[UIAlertView alloc] initWithTitle:@"Couldn't Log In"
                                         message:@"The username and password you entered don't match."
                                        delegate:aDelegate
                               cancelButtonTitle:@"Reset password"
                               otherButtonTitles:@"      Try again      ", nil] autorelease];
    default:
      return nil;
  }
}

+ (UIAlertView*)alertWithTemplate:(AlertTemplate)aTemplate {
  return [self alertWithTemplate:aTemplate delegate:nil];
}

@end
