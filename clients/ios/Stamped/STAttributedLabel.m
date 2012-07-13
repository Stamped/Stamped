//
//  STAttributedLabel.m
//  Stamped
//
//  Created by Landon Judkins on 7/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAttributedLabel.h"
#import "TTTAttributedLabel.h"
#import "Util.h"

@interface STAttributedLabel () <TTTAttributedLabelDelegate>

@property (nonatomic, readonly, retain) NSArray<STActivityReference>* references;

@end

@implementation STAttributedLabel

@synthesize referenceDelegate = _referenceDelegate;
@synthesize references = _references;

- (id)initWithAttributedString:(NSAttributedString*)string width:(CGFloat)width andReferences:(NSArray<STActivityReference>*)references
{
    CGSize size = [Util sizeForString:string thatFits:CGSizeMake(width, CGFLOAT_MAX)];
    self = [super initWithFrame:CGRectMake(0, 0, size.width, size.height)];
    if (self) {
        [self setText:string];
        self.userInteractionEnabled = YES;
        self.delegate = self;
        self.backgroundColor = [UIColor clearColor];
        _references = [references retain];
        if (references.count > 0) { 
            self.linkAttributes = [NSDictionary dictionary];
            for (NSInteger i = 0; i < references.count; i++) {
                id<STActivityReference> reference = [references objectAtIndex:i];
                if (reference.indices.count == 2) {
                    NSInteger start = [[reference.indices objectAtIndex:0] integerValue];
                    NSInteger end = [[reference.indices objectAtIndex:1] integerValue];
                    NSRange range = NSMakeRange(start, end-start);
                    if (start >= 0 && end > start && end <= string.length) {
                        if (reference.action) {
                            [self addLinkToURL:[NSURL URLWithString:[NSString stringWithFormat:@"%d", i]] withRange:range];
                        }
                    }
                }
            }
        }
    }
    return self;
}

- (void)dealloc
{
    [_references release];
    [super dealloc];
}

- (void)attributedLabel:(TTTAttributedLabel *)label didSelectLinkWithURL:(NSURL *)url {
    NSString* string = [url absoluteString];
    if (![string isEqualToString:@"-1"]) {
        id<STActivityReference> reference = [self.references objectAtIndex:[string integerValue]];
        if (self.referenceDelegate && [self.referenceDelegate respondsToSelector:@selector(attributedLabel:didSelectReference:)]) {
            [self.referenceDelegate attributedLabel:self didSelectReference:reference];
        }
    }
}

@end
