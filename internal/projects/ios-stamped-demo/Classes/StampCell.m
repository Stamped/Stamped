//
//  StampCell.m
//  Stamped
//
//  Created by Kevin Palms on 2/9/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "StampCell.h"


@implementation StampCell

@synthesize stampCellTitle, stampCellUsers, stampCellType, stampCellDate, stampCellImage;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier
{
	if (self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])
	{
		
		UIView *cellView = self.contentView;
//		cellView.backgroundColor = [UIColor lightGrayColor];
		
		// TYPE
		stampCellType = [[UILabel alloc] initWithFrame:CGRectMake(81, 14, 100, 18)];
		[stampCellType setTextColor:[UIColor blackColor]];
		[stampCellType setHighlightedTextColor:[UIColor whiteColor]];
		[stampCellType setBackgroundColor:[UIColor clearColor]];
		stampCellType.font = [UIFont boldSystemFontOfSize:13];
		
		[cellView addSubview:stampCellType];
		[stampCellType release];
		
		// DATE
		stampCellDate = [[UILabel alloc] initWithFrame:CGRectMake([[UIScreen mainScreen] applicationFrame].size.width - 75, 14, 65, 18)];
		[stampCellDate setTextColor:[UIColor lightGrayColor]];
		[stampCellDate setBackgroundColor:[UIColor clearColor]];
		stampCellDate.font = [UIFont systemFontOfSize:13];
		stampCellDate.textAlignment = UITextAlignmentRight;
		
		[cellView addSubview:stampCellDate];
		[stampCellDate release];
		
		
		// TITLE
		stampCellTitle = [[UILabel alloc] initWithFrame:CGRectMake(80, 32, [[UIScreen mainScreen] applicationFrame].size.width - 90, 24)];
		[stampCellTitle setTextColor:[UIColor blackColor]];
		[stampCellTitle setHighlightedTextColor:[UIColor whiteColor]];
		[stampCellTitle setBackgroundColor:[UIColor clearColor]];
		stampCellTitle.font = [UIFont boldSystemFontOfSize:22];
		
		[cellView addSubview:stampCellTitle];
		[stampCellTitle release];
		
		// USER
		stampCellUsers = [[UILabel alloc] initWithFrame:CGRectMake(81, 56, 100, 18)];
		[stampCellUsers setTextColor:[UIColor blackColor]];
		[stampCellUsers setHighlightedTextColor:[UIColor whiteColor]];
		[stampCellUsers setBackgroundColor:[UIColor clearColor]];
		stampCellUsers.font = [UIFont boldSystemFontOfSize:13];
		
		[cellView addSubview:stampCellUsers];
		[stampCellUsers release];
		
		// IMAGE
		stampCellImage = [[UIImageView alloc] initWithFrame:CGRectMake(10, 14, 60, 60)];
		[cellView addSubview:stampCellImage];
		[stampCellImage release];
	}
	
	return self;
}

+ (UIImage *)imageThumbnailForStampId:(NSNumber *)stampId
{
	
	NSString *thumbnail = ([[UIScreen mainScreen] respondsToSelector:@selector(scale)] && [[UIScreen mainScreen] scale] == 2) ? [NSString stringWithFormat:@"e-%@-2x", stampId] : [NSString stringWithFormat:@"e-%@", stampId];
	
	if ([[NSFileManager defaultManager] fileExistsAtPath:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]]) {
		return [UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:thumbnail ofType:@"png"]];
	}
	
	return nil;
}

+ (NSString *)timestampFromDateStamped:(NSDate *)dateStamped
{
	
	NSTimeInterval timeSpan = [[NSDate date] timeIntervalSinceDate:dateStamped];
	
	NSString *stampCellTime = nil;
	
	// Minutes
	if (timeSpan < 3540) { stampCellTime = [NSString stringWithFormat:@"%i min", (int)round(timeSpan / 60)]; }
	
	// 1 Hour
	else if (timeSpan < 5400) { stampCellTime = @"1 hour"; }
	
	// Hours
	else if (timeSpan < 86400) { stampCellTime = [NSString stringWithFormat:@"%i hours", (int)round(timeSpan / 3600)]; }
	
	// 1 Day
	else if (timeSpan < 129600) { stampCellTime = @"1 day"; }
	
	// Days
	else if (timeSpan < 2592000) { stampCellTime = [NSString stringWithFormat:@"%i days", (int)round(timeSpan / 86400)]; }
	
	// Within 1 year
	else if (timeSpan < 31449600) {
		NSDateFormatter *dateFormat = [[NSDateFormatter alloc] init];
		[dateFormat setDateFormat:@"MMM d"];
		stampCellTime = [NSString stringWithFormat:@"%@", [dateFormat stringFromDate:dateStamped]];
		[dateFormat release];
	}
	
	// More than 1 year
	else {
		NSDateFormatter *dateFormat = [[NSDateFormatter alloc] init];
		[dateFormat setDateFormat:@"MMM d YY"];
		stampCellTime = [NSString stringWithFormat:@"%@", [dateFormat stringFromDate:dateStamped]];
		[dateFormat release];
	}
	
	//NSLog(@"Time: %@", stampCellTime);
	
	return stampCellTime;
}

@end
