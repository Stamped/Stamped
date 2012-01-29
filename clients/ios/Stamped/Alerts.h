//
//  Alerts.h
//  Stamped
//
//  Created by Jake Zien on 11/9/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

typedef enum {
  AlertTemplateDefault = 0,
  AlertTemplateNoInternet,
  AlertTemplateTimedOut,
  AlertTemplateAlreadyStamped,
  AlertTemplateWebViewFail,
  AlertTemplateInvalidLogin,
  AlertTemplateInvalidSignup,
  AlertTemplateFieldRequired,
  AlertTemplateDuplicateTodo
} AlertTemplate;

@interface Alerts : NSObject {
  NSDate* lastAlertDate;
}

+ (UIAlertView*)alertWithTemplate:(AlertTemplate)aTemplate;
+ (UIAlertView*)alertWithTemplate:(AlertTemplate)aTemplate delegate:(id)aDelegate;

@end
