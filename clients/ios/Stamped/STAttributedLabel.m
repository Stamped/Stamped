//
//  STAttributedLabel.m
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAttributedLabel.h"
#import "STActionManager.h"

@interface STAttributedLabel () <TTTAttributedLabelDelegate>

@property (nonatomic, readonly, copy) NSArray<STActivityReference>* references;

@end

@implementation STAttributedLabel

@synthesize references = _references;

- (id)initWithAttributedString:(NSAttributedString*)string maximumSize:(CGSize)size {
    return [self initWithAttributedString:string maximumSize:size andReferences:[NSArray array]];
}

- (id)initWithAttributedString:(NSAttributedString*)string maximumSize:(CGSize)maximumSize andReferences:(NSArray<STActivityReference>*)references {
    CGSize size = [Util sizeForString:string thatFits:maximumSize];
    self = [super initWithFrame:CGRectMake(0, 0, size.width, size.height)];
    if (self) {
        _references = [references copy];
        self.backgroundColor = [UIColor clearColor];
        self.userInteractionEnabled = YES;
        self.dataDetectorTypes = UIDataDetectorTypeLink;
        self.lineBreakMode = UILineBreakModeWordWrap;
        self.text = string;
        self.delegate = self;
        //    self.layer.shadowColor = [UIColor whiteColor].CGColor;
        //    self.layer.shadowOpacity = .6;
        //    self.layer.shadowOffset = CGSizeMake(0, 1);
        //    self.layer.shadowRadius = 0;
        if (references.count > 0) { 
            for (NSInteger i = 0; i < references.count; i++) {
                id<STActivityReference> reference = [references objectAtIndex:i];
                if (reference.indices.count == 2) {
                    NSInteger start = [[reference.indices objectAtIndex:0] integerValue];
                    NSInteger end = [[reference.indices objectAtIndex:1] integerValue];
                    NSRange range = NSMakeRange(start, end-start);
                    if (end <= string.length) {
                        NSString* key = [NSString stringWithFormat:@"%d", i];
                        [self addLinkToURL:[NSURL URLWithString:key] withRange:range];
                    }
                }
            }
        }
    }
    return self;
}


- (void)attributedLabel:(TTTAttributedLabel*)label didSelectLinkWithURL:(NSURL*)url {
    NSString* string = [url absoluteString];
    NSInteger index = [string integerValue];
    id<STActivityReference> reference = [self.references objectAtIndex:index];
    if (reference.action) {
        id<STAction> action = reference.action;
        STActionContext* context = [STActionContext contextInView:self];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
}

@end
