//
//  STAttributedLabel.h
//  Stamped
//
//  Created by Landon Judkins on 7/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "TTTAttributedLabel.h"
#import "STActivityReference.h"

@protocol STAttributedLabelDelegate;

@interface STAttributedLabel : TTTAttributedLabel

- (id)initWithAttributedString:(NSAttributedString*)string width:(CGFloat)width andReferences:(NSArray<STActivityReference>*)references;

@property (nonatomic, readwrite, assign) id<STAttributedLabelDelegate> referenceDelegate;

@end

@protocol STAttributedLabelDelegate <NSObject>
@optional

- (void)attributedLabel:(STAttributedLabel*)label didSelectReference:(id<STActivityReference>)reference;

@end