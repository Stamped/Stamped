//
//  STAttributedLabel.h
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STActivityReference.h"
#import "TTTAttributedLabel.h"

@interface STAttributedLabel : TTTAttributedLabel

- (id)initWithAttributedString:(NSAttributedString*)string maximumSize:(CGSize)size;

- (id)initWithAttributedString:(NSAttributedString*)string maximumSize:(CGSize)maximumSize andReferences:(NSArray<STActivityReference>*)references;

@end
