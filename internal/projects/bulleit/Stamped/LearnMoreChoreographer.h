//
//  LearnMoreChoreographer.h
//  Stamped
//
//  Created by Jake Zien on 9/15/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface LearnMoreChoreographer : NSObject <UIScrollViewDelegate> {
  @private 
  NSArray* choreoArray_;
  
}

- (void)addChoreographyForView:(UIView*)view 
                         range:(NSRange)range 
                      property:(NSString*)property 
                    startValue:(id)sVal 
                      endValue:(id)eVal;

@end
