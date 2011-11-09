//
//  Alerts.m
//  Stamped
//
//  Created by Jake Zien on 11/9/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "Alerts.h"

@implementation Alerts

+ (UIAlertView*)alertWithTemplate:(AlertTemplate)template {  
  switch (template) {
    case AlertTemplateDefault:
      return [[[UIAlertView alloc] initWithTitle:@"Oops"
                                   message:@"Something went wrong. Feel free to try again."
                                   delegate:nil
                                   cancelButtonTitle:@"Fair Enough"
                                   otherButtonTitles:nil] autorelease];
    case AlertTemplateOurFault:
      return [[[UIAlertView alloc] initWithTitle:@"We Goofed"
                                         message:@"Something went wrong. Feel free to try again."
                                        delegate:nil
                               cancelButtonTitle:@"Fair Enough"
                               otherButtonTitles:nil] autorelease];
    case AlertTemplateNoInternet:
      return [[[UIAlertView alloc] initWithTitle:@"No Internet Connection"
                                         message:@"Stamped works best when it can get online."
                                        delegate:nil
                               cancelButtonTitle:@"Fair Enough"
                               otherButtonTitles:nil] autorelease];      
    case AlertTemplateTimedOut:
      return [[[UIAlertView alloc] initWithTitle:@"Sorry to keep you waiting."
                                         message:@"Your request timed out. Feel free to try again."
                                        delegate:nil
                               cancelButtonTitle:@"Fair Enough"
                               otherButtonTitles:nil] autorelease];
    default:
      return nil;
  }
}

@end
