//
//  WrappingText.h
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CollapsibleViewController;

@interface WrappingText : UIViewController {
  NSString* text;
}

@property (nonatomic, retain) NSString* text;
@property (nonatomic, retain) IBOutlet UITextView* topTextView;
@property (nonatomic, retain) IBOutlet UITextView* bottomTextView;
@property (nonatomic, assign) CollapsibleViewController* container;

@end
